import discord
from discord.ext import commands
from utils.tts import tts_to_pcm
from config import ELEVEN_VOICES

class TTSCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def play_tts(self, message, voice_name, text):
        if message.author.voice:
            vc = message.guild.voice_client
            if not vc:
                vc = await message.author.voice.channel.connect()

            if vc.is_playing():
                vc.stop()

            audio = await tts_to_pcm(text, ELEVEN_VOICES[voice_name])
            vc.play(audio)
        else:
            await message.channel.send("🔇 You're not in a voice channel!")

    @commands.command(name="listvoices", aliases=["lv"])
    async def list_voices(self, ctx):
        voice_list = "\n".join(f"- `{name}`" for name in ELEVEN_VOICES.keys())
        await ctx.send(f"🗣️ Available TTS voices:\n{voice_list}")

async def setup(bot):
    await bot.add_cog(TTSCog(bot))

