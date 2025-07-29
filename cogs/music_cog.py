import discord
from discord.ext import commands
import os
import asyncio
import logging
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

class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_client = None
        self.queue = []
        self.logger = logging.getLogger(__name__)

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
            self.voice_client = await channel.connect()

        sources = await self.get_audio_sources(query)
        if not sources:
            await ctx.send("Failed to load the audio source.")
            return

        for title, source in sources:
            await self.enqueue_or_play(ctx, title, source)

    async def get_audio_sources(self, query):
        if os.path.isfile(query):
            abs_path = os.path.abspath(query)
            player = discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio(abs_path, **FFMPEG_LOCAL_OPTIONS),
                volume=LOCAL_MP3_VOLUME,
            )
            return [(os.path.basename(abs_path), player)]

        candidate = os.path.join(LOCAL_MP3_FOLDER, query)
        if os.path.isfile(candidate):
            abs_path = os.path.abspath(candidate)
            player = discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio(abs_path, **FFMPEG_LOCAL_OPTIONS),
                volume=LOCAL_MP3_VOLUME,
            )
            return [(os.path.basename(abs_path), player)]

        matched = find_matching_audio(query)
        if matched:
            player = discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio(matched, **FFMPEG_LOCAL_OPTIONS),
                volume=LOCAL_MP3_VOLUME,
            )
            return [(os.path.basename(matched), player)]

        return await self.get_youtube_sources(query)

    async def get_youtube_sources(self, query):
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'noplaylist': False,
            'default_search': 'auto',
        }

        with YoutubeDL(ydl_opts) as ydl:
            target = query if is_url(query) else f"ytsearch1:{query}"
            info = await asyncio.get_event_loop().run_in_executor(
                None, lambda: ydl.extract_info(target, download=False)
            )

        entries = info.get('entries') or [info]
        sources = []
        for entry in entries:
            if not entry:
                continue
            try:
                url = get_best_audio_url(entry)
            except Exception as e:
                self.logger.error("Unable to get audio URL: %s", e)
                continue

            player = discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio(
                    url,
                    before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
                    options="-vn",
                ),
                volume=YOUTUBE_VOLUME,
            )
            title = entry.get('title', 'Unknown Title')
            sources.append((title, player))

        return sources

    async def enqueue_or_play(self, ctx, title, source):
        if self.voice_client.is_playing() or self.queue:
            self.queue.append((title, source))
            await ctx.send(f"Queued: {title}")
        else:
            await self.start_playback(ctx, title, source)

    async def start_playback(self, ctx, title, source):
        # Re-use an existing voice client if available instead of attempting
        # to connect again which can raise ``ClientException`` when a previous
        # connection is still being established.
        self.voice_client = ctx.voice_client or self.voice_client

        if not self.voice_client:
            if ctx.author.voice:
                self.voice_client = await ctx.author.voice.channel.connect()
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
