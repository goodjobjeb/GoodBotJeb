# Discord & API tokens
TOKEN = "DISCORD_BOT_TOKEN"
ELEVEN_API_KEY = "EVELENLABS_API_KEY"
OPEN_DOTA_URL = "https://api.opendota.com/api"

COMMAND_PREFIX = "-"

# Paths
LOCAL_MP3_FOLDER = "local_mp3_files"

# FFmpeg options
FFMPEG_OPTIONS = {
    "options": "-vn"
}

FFMPEG_LOCAL_OPTIONS = {
    "before_options": "-loglevel panic",
    "options": "-vn"
}

# Volume settings
MAX_VOLUME = 1.0
DEFAULT_VOLUME = 0.5
LOCAL_FILE_VOLUME = 0.5

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
