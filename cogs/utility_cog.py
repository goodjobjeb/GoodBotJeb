import os
from discord.ext import commands
from config import LOCAL_MP3_FOLDER
from player.downloader import DownloadManager

ALIASES = {
    'join': ['j'],
    'volume': ['v'],
    'listfiles': ['lf'],
    'download': ['dl']
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

    @commands.command(aliases=ALIASES['listfiles'])
    async def listfiles(self, ctx):
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
