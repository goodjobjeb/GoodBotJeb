import discord
from discord.ext import commands
import logging
import asyncio
import os
from config import TOKEN, COMMAND_PREFIX, LOCAL_MP3_FOLDER, ELEVEN_VOICES
from utils.format_fallback import auto_update_yt_dlp
from utils.tts import tts_to_pcm

# Auto-update yt-dlp at startup
auto_update_yt_dlp()

# Configure logging to output to the terminal
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)

# Ensure the local file folder exists for playback and downloads
os.makedirs(LOCAL_MP3_FOLDER, exist_ok=True)

@bot.event
async def on_ready():
    logging.info("%s has connected to Discord!", bot.user.name)
    # Optionally, list out the available commands
    for command in bot.commands:
        logging.debug("Command available: %s", command.name)

@bot.event
async def on_error(event, *args, **kwargs):
    """
    Custom error handler to catch errors and attempt reconnection.
    """
    logging.error("An error occurred: %s, %s, %s", event, args, kwargs)
    if isinstance(event, discord.errors.ConnectionClosed):
        logging.info("Connection closed, attempting to reconnect...")
        await bot.close()
        await bot.start(TOKEN)  # Reconnect to Discord

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.content.startswith(COMMAND_PREFIX):
        parts = message.content[len(COMMAND_PREFIX):].split(maxsplit=1)
        if parts:
            voice_name = parts[0].lower()
            text = parts[1] if len(parts) > 1 else None
            if voice_name in ELEVEN_VOICES and text:
                tts_cog = bot.get_cog("TTSCog")
                if tts_cog:
                    await tts_cog.play_tts(message, voice_name, text)
                return

    await bot.process_commands(message)

# Load cogs asynchronously
INITIAL_EXTENSIONS = [
    "cogs.music_cog",
    "cogs.tts_cog",
    "cogs.dota2_cog",
    "cogs.utility_cog"
]

async def main():
    async with bot:
        # Attempt to load extensions
        for ext in INITIAL_EXTENSIONS:
            logging.info("Loading extension: %s", ext)
            try:
                await bot.load_extension(ext)
                logging.info("Successfully loaded: %s", ext)
            except Exception as e:
                logging.error("Failed to load extension %s: %s", ext, e)

        await bot.start(TOKEN)

if __name__ == "__main__":
    # Ensure that the bot attempts to reconnect if connection closes
    try:
        asyncio.run(main())
    except discord.errors.ConnectionClosed as e:
        logging.error("Connection closed: %s, attempting to reconnect...", e)
        asyncio.run(main())
