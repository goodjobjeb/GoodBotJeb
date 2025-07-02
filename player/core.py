import logging
import discord
from discord.ext import commands
import youtube_dl
from discord.ext.commands import Context

logger = logging.getLogger("discord")
logger.setLevel(logging.DEBUG)

class MusicPlayer:
    def __init__(self, bot):
        self.bot = bot
        self.voice_client = None
        self.queue = []

    async def resolve(self, query):
        """ Resolves the source for the query """
        logger.debug(f"Resolving: {query}")

        # Handle YouTube URL
        if "youtube.com" in query:
            video_url = query
            ydl_opts = {
                'format': 'bestaudio/best',
                'extractaudio': True,
                'audioquality': 1,
                'outtmpl': 'downloads/%(id)s.%(ext)s',
                'quiet': True,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }

            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                audio_url = info['formats'][0]['url']  # Get best available audio URL
                return audio_url

        # Handle local file
        if query.endswith(".mp3"):
            return query  # Assuming query is a local file path
        return None

    async def play(self, ctx: Context, query: str):
        """ Handles the playback of the resolved audio source """
        source = await self.resolve(query)
        
        if source is None:
            await ctx.send("Could not resolve audio source.")
            return

        # Join voice channel
        if not self.voice_client:
            channel = ctx.author.voice.channel
            self.voice_client = await channel.connect()

        # Start playing the audio
        if isinstance(source, str):  # This can be a local file path
            source = discord.FFmpegPCMAudio(source)
        else:  # It's a YouTube URL (audio stream)
            source = discord.FFmpegPCMAudio(source)

        self.voice_client.play(source, after=self.after_playing)

        # Notify the user
        await ctx.send(f"Now playing: {query}")

    def after_playing(self, error):
        if error:
            logger.error(f"Error occurred: {error}")
        # Automatically disconnect when the song ends
        if self.voice_client and not self.voice_client.is_playing():
            logger.info("Playback finished, disconnecting from voice.")
            self.voice_client.disconnect()

# Setup the bot commands for playing music
bot = commands.Bot(command_prefix="-")

@bot.command()
async def play(ctx: Context, *, query: str):
    """ Command to play audio (YouTube or local files) """
    player = MusicPlayer(bot)
    await player.play(ctx, query)

@bot.event
async def on_ready():
    logger.info(f"{bot.user} has connected to Discord!")

bot.run('YOUR_BOT_TOKEN')
