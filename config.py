import os

def _load_token():
    """Load Discord token from environment variable or token.txt file."""
    token = os.environ.get("DISCORD_BOT_TOKEN")
    if token:
        return token
    token_path = os.path.join(os.path.dirname(__file__), "token.txt")
    if os.path.exists(token_path):
        with open(token_path) as f:
            token = f.read().strip()
            if token:
                return token
    return "DISCORD_BOT_TOKEN"


# Discord & API tokens
TOKEN = _load_token()
ELEVEN_API_KEY = os.environ.get("ELEVEN_API_KEY", "ELEVENLABS_API_KEY")
OPEN_DOTA_URL = "https://api.opendota.com/api"

COMMAND_PREFIX = "-"

# Paths
LOCAL_MP3_FOLDER = "local_mp3_files"

# FFmpeg options
FFMPEG_OPTIONS = {
    "before_options": "-allowed_extensions ALL",
    "options": "-vn"
}

FFMPEG_LOCAL_OPTIONS = {
    "before_options": "-loglevel warning",
    "options": "-vn"
}

# Volume settings
MAX_VOLUME = 1.0

# Default volumes for different audio sources. These values can be
# adjusted at runtime via bot commands.
YOUTUBE_VOLUME = 0.5
LOCAL_MP3_VOLUME = 0.5
TTS_VOLUME = 0.5

# Backwards compatibility for modules that still import these names
DEFAULT_VOLUME = YOUTUBE_VOLUME
LOCAL_FILE_VOLUME = LOCAL_MP3_VOLUME

# Voice map for ElevenLabs (command name -> voice ID)
ELEVEN_VOICES = {
    "ivan": "xII1rrs1K3KV8HVEvxjK",
    "avani": "WTnybLRChAQj0OBHYZg4",
    "morten": "Rmv8zCb2IRE895dK1qWB",
    "anime": "XJ2fW4ybq7HouelYYGcL",
    "anicet": "hgZie8MSRBRgVn6w8BzP"
}

# Discord-to-Steam ID mapping
STEAM_LINKS = {
    "discord_id": "steam_id"   # Discord ID : Steam ID
}
