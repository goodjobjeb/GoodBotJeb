import os
import asyncio
from yt_dlp import YoutubeDL
from config import LOCAL_MP3_FOLDER
import logging
from utils.time import parse_timestamp, validate_timestamp_format

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
                'quiet': True
            }

            if timestamp and validate_timestamp_format(timestamp):
                start, end = parse_timestamp(timestamp)
                options['postprocessor_args'] = [
                    '-ss', str(start),
                    '-to', str(end) if end else ''
                ]

            with YoutubeDL(options) as ydl:
                await ctx.send("Downloading...")
                info = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: ydl.extract_info(url, download=True)
                )

            await ctx.send(f"Downloaded: {info.get('title', 'Unknown')}")
        except Exception as e:
            logging.error("Download failed: %s", e)
            await ctx.send(f"Download failed: {str(e)}")
