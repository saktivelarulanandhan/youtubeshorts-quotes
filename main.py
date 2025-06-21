import os
import random
import platform
import requests
import urllib3
import certifi
from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    TextClip,
    CompositeVideoClip
)
from moviepy.video.fx.all import loop as fx_loop
import moviepy.config as mpy_config
from PIL import Image

# ✅ ImageMagick path setup based on OS
if platform.system() == "Windows":
    mpy_config.change_settings({
        "IMAGEMAGICK_BINARY": "C:/Program Files/ImageMagick-7.1.1-Q16/magick.exe"
    })
else:
    mpy_config.change_settings({
        "IMAGEMAGICK_BINARY": "/usr/bin/convert"
    })

# ✅ Suppress SSL warnings for Pexels (not ideal, but fine in testing/dev)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 🔑 Pexels API key
PEXELS_API_KEY = "krdAD3gKcTPVenfesZWX3dbnI7nzK2vyQoFiMgFYtNJqe5WnJl1eOyx4"


# 🔹 Step 1: Get a random quote
def get_quote():
    try:
        res = requests.get("https://api.quotable.io/random", verify=False)
        res.raise_for_status()
        data = res.json()
        return f"{data['content']} — {data['author']}"
    except Exception as e:
        print("⚠️ Failed to fetch quote:", e)
        return "Stay positive. Work hard. Make it happen. — Unknown"


# 🔹 Step 2: Download a random vertical video from Pexels
def download_video_from_pexels(query="nature"):
    headers = {"Authorization": PEXELS_API_KEY}
    params = {"query": query, "per_page": 10, "orientation": "portrait"}

    print(f"📡 Requesting Pexels videos for: '{query}'...")
    response = requests.get(
        "https://api.pexels.com/videos/search",
        headers=headers,
        params=params,
        verify=certifi.where()
    )

    if response.status_code != 200:
        raise Exception(f"Pexels API failed: {response.status_code} - {response.text}")

    results = response.json().get("videos", [])
    if not results:
        raise Exception("❌ No videos found from Pexels.")

    selected = random.choice(results)
    video_url = selected["video_files"][0]["link"]

    # Download the video
    response = requests.get(video_url, stream=True)
    with open("background.mp4", "wb") as f:
        for chunk in response.iter_content(chunk_size=1024 * 1024):
            f.write(chunk)

    return "background.mp4"


# 🔹 Step 3: Pick random music file from folder
def pick_random_music(folder="music"):
    if not os.path.exists(folder):
        raise Exception(f"⚠️ Music folder not found: {folder}")
    files = [f for f in os.listdir(folder) if f.endswith(".mp3")]
    if not files:
        raise Exception("🎵 No music files found in 'music/' folder.")
    choice = os.path.join(folder, random.choice(files))
    print("🎵 Selected music:", choice)
    return choice


# 🔹 Step 4: Add music to video
def add_background_music(clip, music_path):
    try:
        audio = AudioFileClip(music_path).subclip(0, 60).volumex(0.2)
        return clip.set_audio(audio)
    except Exception as e:
        print("⚠️ Failed to add music:", e)
        return clip


# 🔹 Step 5: Overlay quote text
def add_text_overlay(clip, quote):
    print("🔍 ImageMagick path:", mpy_config.IMAGEMAGICK_BINARY)
    txt = TextClip(
        quote,
        fontsize=50,
        color='white',
        size=(900, None),
        method='caption',
        align='center'
    )
    txt = txt.set_position(('center', 'center')).set_duration(clip.duration)
    return CompositeVideoClip([clip, txt])


# 🔹 Step 6: Final composition and export
def generate_video():
    quote = get_quote()
    print("💬 Quote:", quote)

    video_path = download_video_from_pexels("nature")

    base_clip = VideoFileClip(video_path).subclip(0, 15).resize((1080, 1920), Image.Resampling.LANCZOS)
    trimmed_clip = base_clip.subclip(0, base_clip.duration - 0.1)
    looped_clip = fx_loop(trimmed_clip, duration=60)

    clip_with_text = add_text_overlay(looped_clip, quote)
    music_path = pick_random_music("music")
    final_clip = add_background_music(clip_with_text.set_duration(60), music_path)

    output_path = "short_quote.mp4"
    final_clip.write_videofile(output_path, fps=24, codec='libx264', audio_codec='aac')
    print(f"✅ Video created: {output_path}")


if __name__ == "__main__":
    generate_video()
