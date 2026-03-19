import os
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from yt_dlp import YoutubeDL
from config import LOCAL_MP3_FOLDER
from utils.time import parse_timestamp, validate_timestamp_format

_dl_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="dl")


class DownloadManager:
    async def download(self, ctx, url, timestamp=None, filename=None):
        try:
            os.makedirs(LOCAL_MP3_FOLDER, exist_ok=True)
            options = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(LOCAL_MP3_FOLDER, filename or '%(id)s.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'quiet': True,
                'socket_timeout': 15,
            }

            if timestamp and validate_timestamp_format(timestamp):
                start, end = parse_timestamp(timestamp)
                options['postprocessor_args'] = [
                    '-ss', str(start),
                    '-to', str(end) if end else ''
                ]

            await ctx.send("Downloading...")

            def _do_download():
                with YoutubeDL(options) as ydl:
                    return ydl.extract_info(url, download=True)

            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(_dl_executor, _do_download)

            await ctx.send(f"Downloaded: {info.get('title', 'Unknown')}")
        except Exception as e:
            logging.error("Download failed: %s", e)
            await ctx.send(f"Download failed: {str(e)}")
