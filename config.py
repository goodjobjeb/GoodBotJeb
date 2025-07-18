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
