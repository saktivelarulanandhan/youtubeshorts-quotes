import os
import json
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

# === Load OAuth Credentials ===
with open("client_secret.json", "r") as f:
    client_secrets = json.load(f)

with open("token.json") as f:
    credentials_dict = json.load(f)

credentials = Credentials(
    token=credentials_dict["token"],
    refresh_token=credentials_dict["refresh_token"],
    token_uri=client_secrets["installed"]["token_uri"],
    client_id=client_secrets["installed"]["client_id"],
    client_secret=client_secrets["installed"]["client_secret"]
)

youtube = build("youtube", "v3", credentials=credentials)

# === Load quote from file ===
quote_file = "quote.txt"
if os.path.exists(quote_file):
    with open(quote_file, "r", encoding="utf-8") as f:
        quote_text = f.read().strip()
else:
    quote_text = "Here’s your daily dose of inspiration! 💡"

# === Try to extract author if format is "Quote — Author" ===
if "—" in quote_text:
    quote, author = quote_text.split("—", 1)
    quote = quote.strip()
    author = author.strip()
else:
    quote = quote_text
    author = "Unknown"

# === SEO Keywords and Hashtags ===
today = datetime.now().strftime("%B %d, %Y")
primary_keyword = "life changing quote"
hook_phrase = "This quote will change your mindset 💭"
hashtags = ["#shorts", "#motivation", "#quotes", "#inspiration", "#mindset", "#positivity"]
youtube_channel = "https://www.youtube.com/@yourchannelname"

# === SEO-Optimized Title and Description ===
title = f"{hook_phrase} | #{primary_keyword.replace(' ', '')}"
description = f"""✨ "{quote}" — {author}

Start your day with powerful wisdom 💡
🎯 Thought of the Day: {quote}

👉 Subscribe for more inspiring content: {youtube_channel}
💬 What does this quote mean to you? Share your thoughts below!
📅 Uploaded on: {today}

📌 Topics: {primary_keyword}, motivation, daily quote, mindset, growth, inspiration

{" ".join(hashtags)}
"""

# === Tags ===
tags = [
    "shorts", "life changing quote", "quote of the day", "motivational shorts",
    "inspirational shorts", "daily quotes", "mindset shift", "motivationalquote",
    "positivity", "self improvement", "wisdom", "viralshorts", "success", "growth", "selfcare"
]

# === Video Metadata ===
video_metadata = {
    "snippet": {
        "title": title,
        "description": description,
        "tags": tags,
        "categoryId": "22"  # People & Blogs
    },
    "status": {
        "privacyStatus": "public"
    }
}

# === Upload ===
video_file = "short_quote.mp4"
if not os.path.exists(video_file):
    raise FileNotFoundError(f"❌ Video file not found: {video_file}")

# Rename video file with SEO keywords
seo_filename = f"{primary_keyword.replace(' ', '_')}_{today.replace(' ', '_')}.mp4"
os.rename(video_file, seo_filename)

media = MediaFileUpload(seo_filename, chunksize=-1, resumable=True, mimetype="video/*")
upload_request = youtube.videos().insert(
    part="snippet,status",
    body=video_metadata,
    media_body=media
)

print("🚀 Starting upload...")
response = None
while response is None:
    status, response = upload_request.next_chunk()
    if status:
        print(f"📤 Uploading... {int(status.progress() * 100)}%")

print("✅ Upload complete!")
print(f"🎥 Video ID: {response['id']}")
print(f"🔗 Watch at: https://www.youtube.com/watch?v={response['id']}")
