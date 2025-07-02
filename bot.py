import discord
from discord.ext import commands
import logging
import asyncio
import os
from config import TOKEN, COMMAND_PREFIX, LOCAL_MP3_FOLDER
from utils.format_fallback import auto_update_yt_dlp

# Auto-update yt-dlp at startup
auto_update_yt_dlp()

# Configure logging to output to the terminal
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")

# Configure logging
#logging.basicConfig(level=logging.DEBUG)  # Set to DEBUG to capture all logs
#logger = logging.getLogger("discord")
#logger.setLevel(logging.DEBUG)  # Set to DEBUG to capture all logs

# Create a console handler to log to the console
#console_handler = logging.StreamHandler()
#console_handler.setLevel(logging.DEBUG)  # Log to console at DEBUG level
#formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
#console_handler.setFormatter(formatter)

# Add the console handler to the logger
#logger.addHandler(console_handler)

# Optionally, create a file handler to log to a file (if you want to save logs for later)
#file_handler = logging.FileHandler('bot_debug.log')  # Logs to 'bot_debug.log'
#file_handler.setLevel(logging.DEBUG)  # Log to file at DEBUG level
#file_handler.setFormatter(formatter)
#logger.addHandler(file_handler)

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
