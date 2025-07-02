import subprocess


def get_best_audio_url(info):
    """Fallback method when preferred format isn't available"""
    formats = info.get('formats', [])

    # Priority list of acceptable formats
    format_priority = [
        {'ext': 'mp3', 'vcodec': 'none'},
        {'ext': 'm4a', 'vcodec': 'none'},
        {'acodec': 'opus'},
        {'acodec': 'mp4a'},
    ]

    for fmt in format_priority:
        matches = [f for f in formats if all(
            f.get(k) == v for k, v in fmt.items()
        ) and f.get('url')]
        if matches:
            return max(matches, key=lambda x: x.get('abr') or 0)['url']

    # Final fallback to any audio format with a URL
    audio_formats = [f for f in formats if f.get('acodec') != 'none' and f.get('url')]
    if audio_formats:
        return max(audio_formats, key=lambda x: x.get('abr') or 0)['url']

    # Raise a more informative error if SABR may be the cause
    raise ValueError("No suitable audio formats found. This video may be affected by YouTube's SABR restrictions.")

def is_url(string):
    return string.startswith("http://") or string.startswith("https://")

def auto_update_yt_dlp():
    try:
        result = subprocess.run(["yt-dlp", "-U"], capture_output=True, text=True)
        if result.returncode == 0:
            print("yt-dlp update check complete.")
        else:
            print("yt-dlp update failed:", result.stderr)
    except Exception as e:
        print("Error while updating yt-dlp:", str(e))
