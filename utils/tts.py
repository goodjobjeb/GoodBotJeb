import aiohttp
import tempfile
import discord
from config import ELEVEN_API_KEY, FFMPEG_LOCAL_OPTIONS, TTS_VOLUME

async def tts_to_pcm(text: str, voice_id: str) -> discord.PCMVolumeTransformer:
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": ELEVEN_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.4,
            "similarity_boost": 0.8
        }
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            response.raise_for_status()
            audio_data = await response.read()

    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    temp.write(audio_data)
    temp.close()

    return discord.PCMVolumeTransformer(
        discord.FFmpegPCMAudio(temp.name, **FFMPEG_LOCAL_OPTIONS),
        volume=TTS_VOLUME
    )
