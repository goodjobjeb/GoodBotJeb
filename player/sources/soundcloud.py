from yt_dlp import YoutubeDL
import discord
from config import FFMPEG_OPTIONS, DEFAULT_VOLUME
from utils.format_fallback import get_best_audio_url
from .base import AudioSource

class SoundCloudSource(AudioSource):
    def __init__(self, url, title, stream_url):
        super().__init__(url, title)
        self.stream_url = stream_url

    @classmethod
    async def create(cls, query):
        ydl_opts = {
            "format": "bestaudio/best",
            "quiet": True
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)
            title = info.get("title", "Unknown title")
            stream_url = get_best_audio_url(info)
            return cls(query, title, stream_url)

    async def get_player(self):
        source = discord.FFmpegPCMAudio(
            executable="ffmpeg",
            source=self.stream_url,
            **FFMPEG_OPTIONS
        )
        return discord.PCMVolumeTransformer(source, volume=DEFAULT_VOLUME)
