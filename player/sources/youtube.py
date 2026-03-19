import asyncio
import logging
import subprocess
from concurrent.futures import ThreadPoolExecutor
from yt_dlp import YoutubeDL
import discord
from utils.format_fallback import get_best_audio_url

logger = logging.getLogger(__name__)

_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="yt-src")


class YouTubeSource:
    @classmethod
    async def create_source(cls, query):
        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': False,
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'default_search': 'auto',
            'socket_timeout': 10,
        }

        loop = asyncio.get_event_loop()

        def _extract():
            with YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(query, download=False)

        try:
            info = await loop.run_in_executor(_executor, _extract)
            if 'entries' in info:
                return [cls(entry) for entry in info['entries'] if entry]
            return [cls(info)]
        except Exception as e:
            logger.error("Error extracting YouTube info: %s", e)
            return None

    def __init__(self, info):
        self.title = info.get("title", "Unknown Title")
        self.url = get_best_audio_url(info)

    async def get_player(self):
        return discord.FFmpegPCMAudio(
            source=self.url,
            executable="ffmpeg",
            stderr=subprocess.PIPE,
            before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -allowed_extensions ALL",
            options="-vn"
        )
