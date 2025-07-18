import os
from discord.ext import commands
import config
from config import (
    LOCAL_MP3_FOLDER,
    MAX_VOLUME,
    YOUTUBE_VOLUME,
    LOCAL_MP3_VOLUME,
    TTS_VOLUME,
)
from player.downloader import DownloadManager

ALIASES = {
    'join': ['j'],
    'volume': ['v'],
    'listfiles': ['lf'],
    'download': ['dl'],
    'ytvolume': ['ytv'],
    'localmp3volume': ['lmp3v'],
    'ttsvolume': ['ttsv'],
}

downloader = DownloadManager()

class UtilityCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=ALIASES['join'])
    async def join(self, ctx):
        if ctx.author.voice:
            if not ctx.voice_client:
                await ctx.author.voice.channel.connect()
            elif ctx.voice_client.channel != ctx.author.voice.channel:
                await ctx.voice_client.move_to(ctx.author.voice.channel)

    @commands.command(aliases=ALIASES['volume'])
    async def volume(self, ctx, vol: float):
        vc = ctx.voice_client
        if vc and vc.source:
            vc.source.volume = min(vol, 1.0)
            await ctx.send(f"🔊 Volume set to {vol}")
        else:
            await ctx.send("⚠️ No audio source is playing.")

    @commands.command(aliases=ALIASES['ytvolume'])
    async def youtubevolume(self, ctx, vol: float):
        config.YOUTUBE_VOLUME = min(vol, MAX_VOLUME)
        config.DEFAULT_VOLUME = config.YOUTUBE_VOLUME
        await ctx.send(f"🎵 YouTube volume set to {config.YOUTUBE_VOLUME}")

    @commands.command(aliases=ALIASES['localmp3volume'])
    async def localmp3volume(self, ctx, vol: float):
        config.LOCAL_MP3_VOLUME = min(vol, MAX_VOLUME)
        config.LOCAL_FILE_VOLUME = config.LOCAL_MP3_VOLUME
        await ctx.send(f"📁 Local MP3 volume set to {config.LOCAL_MP3_VOLUME}")

    @commands.command(aliases=ALIASES['ttsvolume'])
    async def ttsvolume(self, ctx, vol: float):
        config.TTS_VOLUME = min(vol, MAX_VOLUME)
        await ctx.send(f"🗣️ TTS volume set to {config.TTS_VOLUME}")

    @commands.command(aliases=ALIASES['listfiles'])
    async def listfiles(self, ctx):
        if not os.path.isdir(LOCAL_MP3_FOLDER):
            await ctx.send("Local MP3 folder does not exist.")
            return

        files = [f for f in os.listdir(LOCAL_MP3_FOLDER) if f.endswith('.mp3')]
        if files:
            await ctx.send("📂 Local MP3 files:\n" + "\n".join(files[:25]))
        else:
            await ctx.send("No MP3 files found.")

    @commands.command(aliases=ALIASES['download'])
    async def download(self, ctx, url: str, timestamp: str = None, filename: str = None):
        await downloader.download(ctx, url, timestamp, filename)

async def setup(bot):
    await bot.add_cog(UtilityCog(bot))
