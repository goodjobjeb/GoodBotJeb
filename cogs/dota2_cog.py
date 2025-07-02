from discord.ext import commands
from utils import dota2
from config import STEAM_LINKS
from utils.tts import tts_to_pcm

class Dota2Cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="dota2")
    async def dota2_roast(self, ctx):
        discord_id = str(ctx.author.id)
        steam_id = STEAM_LINKS.get(discord_id)
        if not steam_id:
            await ctx.send("⚠️ Steam ID not linked.")
            return

        match = await dota2.latest_match(steam_id)
        if not match:
            await ctx.send("No recent match found.")
            return

        players = await dota2.match_players(match["match_id"])
        roast_lines = []
        for p in players:
            discord_id = next((k for k, v in STEAM_LINKS.items() if v == str(p["account_id"])), None)
            if discord_id:
                user = await ctx.guild.fetch_member(int(discord_id))
                name = user.display_name
                hero = await dota2.hero_name(p["hero_id"])
                kda = (p["kills"] + p["assists"]) / max(1, p["deaths"])
                roast_lines.append(dota2.trash_talk_line(name, kda, hero))

        if not roast_lines:
            await ctx.send("No linked players found in recent match.")
            return

        text = " ".join(roast_lines)
        audio = await tts_to_pcm(text, voice_id="your-default-voice-id")
        if not ctx.voice_client:
            await ctx.author.voice.channel.connect()
        ctx.voice_client.play(audio)
        await ctx.send("🧨 Roast delivered!")

async def setup(bot):
    await bot.add_cog(Dota2Cog(bot))
