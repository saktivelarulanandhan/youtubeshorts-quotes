import requests
import random
import os
from moviepy.editor import *
from PIL import Image
import certifi
import urllib3
from moviepy.video.fx.all import loop as fx_loop
from moviepy.editor import AudioFileClip
import moviepy.config as mpy_config
mpy_config.change_settings({"IMAGEMAGICK_BINARY": "C:/Program Files/ImageMagick-7.1.1-Q16/magick.exe"})


# Suppress warnings if using verify=False (TEMP)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

PEXELS_API_KEY = "krdAD3gKcTPVenfesZWX3dbnI7nzK2vyQoFiMgFYtNJqe5WnJl1eOyx4"

# Step 1: Get a random quote
def get_quote():
    res = requests.get("https://api.quotable.io/random", verify=False)
    data = res.json()
    return f"{data['content']} — {data['author']}"

# Step 2: Download video from Pexels
def download_video_from_pexels(query="nature"):
    headers = {"Authorization": PEXELS_API_KEY}
    params = {"query": query, "per_page": 10, "orientation": "portrait"}
    print(f"📡 Requesting Pexels videos for: '{query}'...")
    response = requests.get("https://api.pexels.com/videos/search", headers=headers, params=params, verify=certifi.where())
    results = response.json().get("videos", [])
    if not results:
        raise Exception("No videos found.")
    
    selected = random.choice(results)
    video_url = selected["video_files"][0]["link"]
    
    response = requests.get(video_url, stream=True)
    with open("background.mp4", "wb") as f:
        for chunk in response.iter_content(chunk_size=1024 * 1024):
            f.write(chunk)

    return "background.mp4"

def pick_random_music(folder="music"):
    files = [f for f in os.listdir(folder) if f.endswith(".mp3")]
    if not files:
        raise Exception("No music files found in 'music/' folder.")
    choice = os.path.join(folder, random.choice(files))
    print("🎵 Selected local music:", choice)
    return choice

def add_background_music(clip, music_path):
    try:
        audio = AudioFileClip(music_path).volumex(0.2)
        return clip.set_audio(audio)
    except Exception as e:
        print("⚠️ Failed to add music:", e)
        return clip

# Step 4: Overlay quote
def add_text_overlay(clip, quote):
    txt = TextClip(quote, fontsize=50, color='white', size=(900, None), method='caption', align='center')
    txt = txt.set_position(('center', 'center')).set_duration(clip.duration)
    return CompositeVideoClip([clip, txt])

# Step 5: Generate full video
def generate_video():
    quote = get_quote()
    print("Quote:", quote)

    video_path = download_video_from_pexels("nature")

    # Load and resize base video
    base_clip = VideoFileClip(video_path).subclip(0, 15).resize((1080, 1920), Image.Resampling.LANCZOS)

    # 🔁 Smooth loop: trim tiny bit to avoid repeated last frame
    trimmed_clip = base_clip.subclip(0, base_clip.duration - 0.1)

    # Loop cleanly to 60 seconds
    looped_clip = fx_loop(trimmed_clip, duration=60)

    # 📝 Add quote overlay
    clip_with_text = add_text_overlay(looped_clip.set_duration(60), quote)

    # 🎵 Pick and trim music to 60s
    music_path = pick_random_music("music")
    audio = AudioFileClip(music_path).subclip(0, 60).volumex(0.2)

    # 🔗 Combine audio + video
    final_clip = clip_with_text.set_audio(audio)

    # 💾 Export
    output_path = "short_quote.mp4"
    final_clip.write_videofile(output_path, fps=24, codec='libx264', audio_codec='aac')
    print(f"✅ Generated video: {output_path}")


if __name__ == "__main__":
    generate_video()
