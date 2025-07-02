import os
import random
import difflib
from config import LOCAL_MP3_FOLDER

def find_matching_audio(query):
    query = query.lower().strip()
    query = os.path.splitext(query)[0]  # Remove .mp3 extension if present

    matches = []
    close_matches = []

    for root, _, files in os.walk(LOCAL_MP3_FOLDER):
        for file in files:
            if file.lower().endswith('.mp3'):
                rel_path = os.path.relpath(os.path.join(root, file), LOCAL_MP3_FOLDER)
                base_name = os.path.splitext(file)[0].lower()
                rel_base = os.path.splitext(rel_path)[0].lower()

                if base_name == query or rel_base == query:
                    return os.path.join(root, file)
                else:
                    close_matches.append((file, base_name, rel_base))

    suggestions = difflib.get_close_matches(query, [b for _, b, _ in close_matches], n=1, cutoff=0.6)
    if suggestions:
        print(f"[find_matching_audio] Did you mean: {suggestions[0]}?")

    print(f"[find_matching_audio] No exact match found for '{query}'")
    return None

def get_random_file_from_folder(folder_name):
    folder_path = os.path.join(LOCAL_MP3_FOLDER, folder_name)
    if not os.path.exists(folder_path):
        return None

    mp3s = [f for f in os.listdir(folder_path) if f.lower().endswith('.mp3')]
    return os.path.join(folder_path, random.choice(mp3s)) if mp3s else None
