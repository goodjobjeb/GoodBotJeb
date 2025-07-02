import aiohttp
import random
from config import OPEN_DOTA_URL

HERO_NAMES = {}

async def _get_json(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.json()

async def hero_name(hero_id: int):
    if not HERO_NAMES:
        data = await _get_json(f"{OPEN_DOTA_URL}/heroes")
        HERO_NAMES.update({h["id"]: h["localized_name"] for h in data})
    return HERO_NAMES.get(hero_id, f"Hero#{hero_id}")

async def latest_match(steam_id: str):
    games = await _get_json(f"{OPEN_DOTA_URL}/players/{steam_id}/recentMatches")
    return games[0] if games else None

async def match_players(match_id: int):
    return await _get_json(f"{OPEN_DOTA_URL}/matches/{match_id}")

def trash_talk_line(name: str, kda: float, hero: str) -> str:
    if kda < 1.0:
        return random.choice([
            f"{name} was playing {hero}, but it looked more like feeding simulator 2025.",
            f"{name} on {hero}? I've seen bots with better map awareness.",
            f"{name} made {hero} look like a support punching bag."
        ])
    elif kda < 2.5:
        return random.choice([
            f"{name} was just there for moral support on {hero}... and failed at that too.",
            f"{hero} must be crying after what {name} just did to it.",
            f"{name} really redefined mediocrity on {hero}."
        ])
    else:
        return random.choice([
            f"Okay fine, {name} was decent on {hero}, even if it hurt to admit.",
            f"{name} actually made {hero} look competent. Did someone else play for them?",
            f"I’d roast {name} for {hero}, but they kinda clutched it. This time."
        ])
