import discord
from discord.ext import commands
import yt_dlp
import os

class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_client = None

    @commands.command()
    async def play(self, ctx, url):
        # Ensure the user is connected to a voice channel
        if not ctx.author.voice:
            await ctx.send("You must join a voice channel first.")
            return
        
        channel = ctx.author.voice.channel
        if self.voice_client is None:
            self.voice_client = await channel.connect()

        # Get audio from YouTube or local file
        audio_source = await self.get_audio_source(url)
        if audio_source:
            self.voice_client.play(audio_source, after=lambda e: print(f"Finished playing: {e}"))
            await ctx.send(f"Now playing: {url}")
        else:
            await ctx.send("Failed to load the audio source.")

    async def get_audio_source(self, url):
        if url.startswith("http"):  # Handle YouTube URL
            return await self.get_youtube_audio_source(url)
        
        if os.path.isfile(url):  # Handle local files
            abs_path = os.path.abspath(url)
            return discord.FFmpegPCMAudio(abs_path)

        return None  # Invalid URL or file

    async def get_youtube_audio_source(self, url):
        # Ensure the downloads directory exists
        os.makedirs('downloads', exist_ok=True)

        # Setup yt-dlp options
        ydl_opts = {
            'format': 'bestaudio/best',
            'extractaudio': True,
            'audioquality': 1,
            'outtmpl': 'downloads/%(id)s.%(ext)s',
            'quiet': False,  # Disable quiet mode
            'logtostderr': True,  # Enable logging
            'postprocessors': [{
                'key': 'FFmpegAudioConvertor',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                base, _ = os.path.splitext(filename)
                mp3_filename = base + '.mp3'

                if os.path.exists(mp3_filename):
                    return discord.FFmpegPCMAudio(mp3_filename)
                else:
                    print(f"Failed to download or convert the audio file from YouTube.")
                    return None
            except Exception as e:
                print(f"Error extracting YouTube audio: {e}")
                return None

    @commands.command()
    async def stop(self, ctx):
        if self.voice_client:
            self.voice_client.stop()
            await self.voice_client.disconnect()
            await ctx.send("Music stopped and disconnected.")
        else:
            await ctx.send("I'm not playing any music right now.")

async def setup(bot):
    await bot.add_cog(MusicCog(bot))
