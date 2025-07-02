import logging
import subprocess
from yt_dlp import YoutubeDL
import discord
from utils.format_fallback import get_best_audio_url

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

class YouTubeSource:
    @classmethod
    async def create_source(cls, query):
        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': False,
            'quiet': True,
            'extract_flat': False,
            'default_search': 'auto',
        }

        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(query, download=False)
                if 'entries' in info:
                    return [cls(entry) for entry in info['entries'] if entry]
                return [cls(info)]
        except Exception as e:
            logger.error(f"Error extracting YouTube info: {e}")
            return None

    def __init__(self, info):
        self.title = info.get("title", "Unknown Title")
        self.url = get_best_audio_url(info)

    async def get_player(self):
        return discord.FFmpegPCMAudio(
            source=self.url,
            executable="ffmpeg",
            stderr=subprocess.PIPE,
            before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            options="-vn"
        )
