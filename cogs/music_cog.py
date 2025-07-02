import discord
from discord.ext import commands
import yt_dlp
import os
import logging
from config import LOCAL_MP3_FOLDER, FFMPEG_LOCAL_OPTIONS, LOCAL_FILE_VOLUME
from utils.audio import find_matching_audio

ALIASES = {
    'play': ['p'],
    'skip': ['s']
}

class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_client = None
        self.logger = logging.getLogger(__name__)

    @commands.command(aliases=ALIASES['play'])
    async def play(self, ctx, *, query: str):
        # Ensure the user is connected to a voice channel
        if not ctx.author.voice:
            await ctx.send("You must join a voice channel first.")
            return
        
        channel = ctx.author.voice.channel
        if self.voice_client is None:
            self.voice_client = await channel.connect()

        # Get audio from YouTube or local file
        audio_source = await self.get_audio_source(query)
        if audio_source:
            try:
                self.voice_client.play(
                    audio_source,
                    after=lambda e: self.logger.error("Playback error: %s", e) if e else None
                )
                await ctx.send(f"Now playing: {query}")
            except Exception as e:
                self.logger.error("Failed to play audio: %s", e)
                await ctx.send("❌ Error during playback. Check logs for details.")
        else:
            await ctx.send("Failed to load the audio source.")

    async def get_audio_source(self, query):
        if query.startswith("http"):
            return await self.get_youtube_audio_source(query)

        # Direct file path provided
        if os.path.isfile(query):
            abs_path = os.path.abspath(query)
            return discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio(abs_path, **FFMPEG_LOCAL_OPTIONS),
                volume=LOCAL_FILE_VOLUME,
            )

        # Try relative to configured folder
        candidate = os.path.join(LOCAL_MP3_FOLDER, query)
        if os.path.isfile(candidate):
            abs_path = os.path.abspath(candidate)
            return discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio(abs_path, **FFMPEG_LOCAL_OPTIONS),
                volume=LOCAL_FILE_VOLUME,
            )

        # Search the folder tree for a matching file
        matched = find_matching_audio(query)
        if matched:
            return discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio(matched, **FFMPEG_LOCAL_OPTIONS),
                volume=LOCAL_FILE_VOLUME,
            )

        self.logger.warning("No local audio found for query: %s", query)
        return None

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
                    self.logger.error("Failed to download or convert the audio file from YouTube.")
                    return None
            except Exception as e:
                self.logger.error("Error extracting YouTube audio: %s", e)
                return None

    @commands.command(aliases=ALIASES['skip'])
    async def skip(self, ctx):
        if self.voice_client and self.voice_client.is_playing():
            self.voice_client.stop()
            await ctx.send("⏭️ Skipped.")
        else:
            await ctx.send("Nothing is playing.")

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
