import discord
import os
import logging
import asyncio
from config import FFMPEG_LOCAL_OPTIONS, LOCAL_FILE_VOLUME

logger = logging.getLogger(__name__)

class LocalSource:
    def __init__(self, path):
        self.path = path
        self.title = os.path.basename(path)

    @classmethod
    async def create_source(cls, path):
        logger.info(f"[LocalSource] Looking for local file match: {path}")
        if not os.path.exists(path):
            logger.warning(f"[LocalSource] File not found: {path}")
            return None

        logger.info(f"[LocalSource] Found match: {path}")
        return cls(path)

    async def get_player(self):
        if not os.path.exists(self.path):
            logger.warning(f"[LocalSource] File missing at playback: {self.path}")
            return None

        try:
            audio = discord.FFmpegPCMAudio(self.path, **FFMPEG_LOCAL_OPTIONS)
            player = discord.PCMVolumeTransformer(audio, volume=LOCAL_FILE_VOLUME)
            logger.info(f"[LocalSource] Returning PCM transformer for: {self.path}")
            return player
        except Exception as e:
            logger.error(f"[LocalSource] Failed to create player: {e}")
            return None

    async def stream(self, ctx):
        player = await self.get_player()
        if not player:
            await ctx.send("❌ Could not prepare the audio file.")
            return

        def after_playback(error):
            if error:
                logger.error(f"[LocalSource] Playback error: {error}")
            fut = ctx.bot.get_cog("MusicCog").get_player(ctx)._play_next(ctx)
            asyncio.run_coroutine_threadsafe(fut, ctx.bot.loop)

        # Play the file in the voice channel
        ctx.voice_client.play(player, after=after_playback)
        await ctx.send(f"▶️ Now playing: {self.title}")
