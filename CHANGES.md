# Changes — v0.0.15

## Files to delete

- **`player/core.py`** — This file uses the deprecated `youtube_dl` library (not `yt_dlp`), creates its own `bot.run()` call that conflicts with `bot.py`, and duplicates functionality already handled by `cogs/music_cog.py`. Remove it entirely.

## Files changed

### `__init__.py`
- **Bug fix**: Removed `from .bot import MusicBot` — the `MusicBot` class doesn't exist anywhere in the codebase. This import would crash on startup.

### `config.py`
- **Improvement**: Token now loads from the `DISCORD_BOT_TOKEN` environment variable first, then falls back to reading `token.txt`, then falls back to the placeholder string. Same for the ElevenLabs API key (`ELEVEN_API_KEY` env var).

### `bot.py`
- **Bug fix**: Removed the manual `on_error` reconnection handler that called `bot.close()` then `bot.start()` — this caused double-connection issues. The `discord.py` library handles reconnection automatically with `reconnect=True`.
- **Bug fix**: Removed double `asyncio.run(main())` in the `except` block at the bottom — this would fail because the event loop is already closed after the first run.

### `cogs/music_cog.py` (main performance rewrite)
- **Speed**: Added a dedicated `ThreadPoolExecutor(max_workers=4)` for yt-dlp calls. Previously, `run_in_executor(None, ...)` used the default executor which shares threads with everything else.
- **Speed**: Added a URL cache with 30-minute TTL. Replaying the same YouTube link skips extraction entirely.
- **Speed**: Uses `extract_flat='in_playlist'` for playlists — gets the first track metadata instantly instead of resolving all tracks upfront, so playback starts while the rest of the playlist resolves.
- **Speed**: Added `socket_timeout=10` and `no_warnings=True` to yt-dlp options to cut latency on slow servers.
- **Bug fix**: The `get_youtube_sources` method was calling `ydl.extract_info()` directly inside a `with YoutubeDL()` block without `run_in_executor`, blocking the entire event loop during extraction. Now all yt-dlp calls run in the thread pool.

### `player/sources/youtube.py`
- **Speed**: Added `run_in_executor` with a dedicated thread pool — the `create_source` classmethod was blocking the event loop.
- **Cleanup**: Removed manual logger handler setup (was adding duplicate `StreamHandler` instances on every import). Now uses standard `logging.getLogger(__name__)`.

### `player/downloader.py`
- **Speed**: Download now runs in a dedicated thread pool instead of using `asyncio.get_event_loop().run_in_executor(None, ...)`.
- **Speed**: Added `socket_timeout=15` to yt-dlp options.

### `player/sources/manager.py`
- **Cleanup**: Removed duplicate `StreamHandler` setup. Uses `%s` format strings instead of f-strings in log calls (avoids string formatting when log level is disabled).

## Files unchanged
- `cogs/tts_cog.py`
- `cogs/dota2_cog.py`
- `cogs/utility_cog.py`
- `player/queue.py`
- `player/sources/base.py`
- `player/sources/local.py`
- `player/sources/soundcloud.py`
- `player/sources/spotify.py`
- `player/sources/tiktok.py`
- `player/sources/__init__.py`
- `utils/` (all files)
