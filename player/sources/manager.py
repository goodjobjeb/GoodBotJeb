import logging
from player.sources.youtube import YouTubeSource
from player.sources.local import LocalSource
from utils.audio import find_matching_audio

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Set to DEBUG for better error tracking
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

class SourceManager:
    def __init__(self, bot):
        self.bot = bot

    async def resolve(self, query):
        logger.debug(f"Calling resolve with query: {query}")  # Log every call to resolve()
        
        try:
            # Check if the query is a YouTube URL
            if "youtube.com" in query or "youtu.be" in query:
                logger.debug("Detected YouTube URL.")
                return await YouTubeSource.create_source(query)

            # Handle local files
            local_path = find_matching_audio(query)
            if local_path:
                logger.debug(f"Found local file: {local_path}")
                return await LocalSource.create_source(local_path)

        except Exception as e:
            logger.error(f"Error resolving source: {e}")
            return None
