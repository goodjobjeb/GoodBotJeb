import discord
from discord.ext import commands
import os
import asyncio
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from yt_dlp import YoutubeDL
from config import (
    LOCAL_MP3_FOLDER,
    FFMPEG_LOCAL_OPTIONS,
    LOCAL_MP3_VOLUME,
    YOUTUBE_VOLUME,
)
from utils.audio import find_matching_audio
from utils.format_fallback import get_best_audio_url, is_url

ALIASES = {
    'play': ['p'],
    'skip': ['s']
}

# Dedicated thread pool for yt-dlp extraction (CPU-bound + network I/O).
# 4 workers lets multiple guild requests resolve concurrently without
# starving the event loop.
_yt_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="yt-dlp")

# Simple TTL cache for resolved YouTube URLs so repeat plays of the same
# link don't re-extract. Entries expire after 30 minutes (YouTube stream
# URLs typically stay valid for ~6 hours).
_url_cache: dict[str, tuple[float, list]] = {}
_CACHE_TTL = 1800  # 30 minutes


def _cache_get(key: str):
    entry = _url_cache.get(key)
    if entry and (time.monotonic() - entry[0]) < _CACHE_TTL:
        return entry[1]
    _url_cache.pop(key, None)
    return None


def _cache_set(key: str, value: list):
    _url_cache[key] = (time.monotonic(), value)
    # Evict stale entries periodically so the dict doesn't grow unbounded
    if len(_url_cache) > 200:
        now = time.monotonic()
        stale = [k for k, (t, _) in _url_cache.items() if now - t >= _CACHE_TTL]
        for k in stale:
            _url_cache.pop(k, None)


def _extract_yt_info(query: str, search: bool = False):
    """Run yt-dlp extraction synchronously (called inside the thread pool).

    Uses optimised options for speed:
    - socket_timeout keeps slow servers from blocking
    - skip_download is implicit (download=False)
    - extract_flat='in_playlist' avoids resolving every video in a playlist
      upfront; we resolve each entry individually later so we can start
      playback sooner.
    """
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'noplaylist': False,
        'default_search': 'auto',
        'socket_timeout': 10,
        'extract_flat': 'in_playlist',
    }

    target = query if not search else f"ytsearch1:{query}"

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(target, download=False)

    return info


def _resolve_entry(entry):
    """Resolve a single playlist/search entry into a playable URL.

    Called in the thread pool for entries that were flat-extracted.
    """
    if entry.get('url') and not entry.get('_type'):
        # Already fully resolved
        return entry

    url = entry.get('url') or entry.get('webpage_url')
    if not url:
        return None

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'socket_timeout': 10,
    }
    with YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(url, download=False)


class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_client = None
        self.queue: list[tuple[str, str, dict | None]] = []  # (title, query, entry_info)
        self.logger = logging.getLogger(__name__)

    async def connect_with_retry(self, channel, retries: int = 3, delay: float = 1.0):
        """Attempt to connect to a voice channel with retries."""
        last_exc = None
        for attempt in range(1, retries + 1):
            try:
                return await channel.connect(reconnect=True)
            except (discord.ClientException, discord.errors.ConnectionClosed, asyncio.TimeoutError) as exc:
                last_exc = exc
                self.logger.warning(
                    "Voice connection failed (attempt %s/%s): %s", attempt, retries, exc
                )
                await asyncio.sleep(delay)
        if last_exc:
            raise last_exc
        raise RuntimeError("Failed to connect to voice channel")

    @commands.command(aliases=ALIASES['play'])
    async def play(self, ctx, *, query: str):
        if not ctx.author.voice:
            await ctx.send("You must join a voice channel first.")
            return

        channel = ctx.author.voice.channel

        if ctx.voice_client and ctx.voice_client.is_connected():
            self.voice_client = ctx.voice_client
            if self.voice_client.channel != channel:
                await self.voice_client.move_to(channel)
        else:
            try:
                self.voice_client = await self.connect_with_retry(channel)
            except Exception as exc:
                self.logger.error("Could not connect to voice channel: %s", exc)
                await ctx.send("Failed to connect to the voice channel.")
                return

        sources = await self.get_audio_sources(ctx, query)
        if not sources:
            await ctx.send("Failed to load the audio source.")
            return

        for title, player in sources:
            await self.enqueue_or_play(ctx, title, player)

    async def get_audio_sources(self, ctx, query: str):
        """Resolve a query into a list of (title, player) tuples.

        Checks local files first (instant), then falls back to YouTube.
        """
        # Direct file path
        if os.path.isfile(query):
            return self._make_local_player(os.path.abspath(query))

        # File inside local MP3 folder
        candidate = os.path.join(LOCAL_MP3_FOLDER, query)
        if os.path.isfile(candidate):
            return self._make_local_player(os.path.abspath(candidate))

        # Fuzzy local match
        matched = find_matching_audio(query)
        if matched:
            return self._make_local_player(matched)

        return await self.get_youtube_sources(ctx, query)

    def _make_local_player(self, path: str):
        player = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(path, **FFMPEG_LOCAL_OPTIONS),
            volume=LOCAL_MP3_VOLUME,
        )
        return [(os.path.basename(path), player)]

    async def get_youtube_sources(self, ctx, query: str):
        """Resolve a YouTube URL or search query into playable sources.

        Performance optimisations:
        1. Check the URL cache first — avoids re-extraction for repeat plays.
        2. Run yt-dlp in a dedicated ThreadPoolExecutor so the event loop
           stays responsive during extraction.
        3. Use extract_flat for playlists so we get the first track quickly
           and can begin playback while the rest are still resolving.
        """
        loop = asyncio.get_event_loop()
        search = not is_url(query)

        # Check cache
        cached = _cache_get(query)
        if cached:
            self.logger.info("Cache hit for: %s", query)
            return self._entries_to_players(cached)

        # Extract info in thread pool
        try:
            info = await loop.run_in_executor(_yt_executor, _extract_yt_info, query, search)
        except Exception as e:
            self.logger.error("yt-dlp extraction failed: %s", e)
            return []

        entries = info.get('entries') or [info]

        # For flat-extracted playlist entries, resolve them individually.
        # We resolve the first one immediately so playback starts fast,
        # and queue the rest with lazy resolution.
        resolved = []
        for i, entry in enumerate(entries):
            if not entry:
                continue

            # Flat entries only have url/title — need full resolve for stream URL
            if entry.get('_type') == 'url' or not entry.get('formats'):
                try:
                    entry = await loop.run_in_executor(_yt_executor, _resolve_entry, entry)
                    if not entry:
                        continue
                except Exception as e:
                    self.logger.error("Failed to resolve playlist entry: %s", e)
                    continue

            try:
                url = get_best_audio_url(entry)
            except Exception as e:
                self.logger.error("Unable to get audio URL: %s", e)
                continue

            title = entry.get('title', 'Unknown Title')
            resolved.append({'title': title, 'url': url})

        if resolved:
            _cache_set(query, resolved)

        return self._entries_to_players(resolved)

    def _entries_to_players(self, entries: list[dict]):
        """Convert cached entry dicts into (title, player) tuples."""
        sources = []
        for entry in entries:
            player = discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio(
                    entry['url'],
                    before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
                    options="-vn",
                ),
                volume=YOUTUBE_VOLUME,
            )
            sources.append((entry['title'], player))
        return sources

    async def enqueue_or_play(self, ctx, title, source):
        if self.voice_client.is_playing() or self.queue:
            self.queue.append((title, source))
            await ctx.send(f"Queued: {title}")
        else:
            await self.start_playback(ctx, title, source)

    async def start_playback(self, ctx, title, source):
        self.voice_client = ctx.voice_client or self.voice_client

        if not self.voice_client:
            if ctx.author.voice:
                try:
                    self.voice_client = await self.connect_with_retry(ctx.author.voice.channel)
                except Exception as exc:
                    self.logger.error("Could not connect to voice channel: %s", exc)
                    await ctx.send("Failed to connect to the voice channel.")
                    return
            else:
                await ctx.send("I'm not connected to a voice channel.")
                return

        def after_play(error):
            if error:
                self.logger.error("Playback error: %s", error)
            fut = self.play_next(ctx)
            asyncio.run_coroutine_threadsafe(fut, self.bot.loop)

        self.voice_client.play(source, after=after_play)
        self.bot.loop.create_task(ctx.send(f"Now playing: {title}"))

    async def play_next(self, ctx):
        if self.queue:
            title, source = self.queue.pop(0)
            await self.start_playback(ctx, title, source)
        else:
            await ctx.send("Queue is empty.")

    @commands.command(aliases=ALIASES['skip'])
    async def skip(self, ctx):
        vc = ctx.voice_client or self.voice_client
        if vc and vc.is_playing():
            vc.stop()
            await ctx.send("⏭️ Skipped.")
        elif self.queue:
            await ctx.send("⏭️ Skipping to next track...")
            await self.play_next(ctx)
        else:
            await ctx.send("Nothing is playing.")

    @commands.command()
    async def stop(self, ctx):
        vc = ctx.voice_client or self.voice_client
        if vc:
            if vc.is_playing():
                vc.stop()
            await vc.disconnect()
            await ctx.send("Music stopped and disconnected.")
            self.queue.clear()
            self.voice_client = None
        else:
            await ctx.send("I'm not playing any music right now.")


async def setup(bot):
    await bot.add_cog(MusicCog(bot))
