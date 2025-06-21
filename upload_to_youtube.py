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

# === Detect quote from file or fallback ===
quote_file = "quote.txt"  # Optional: main.py can save quote to this
if os.path.exists(quote_file):
    with open(quote_file, "r", encoding="utf-8") as f:
        quote_text = f.read().strip()
else:
    quote_text = "Here’s your daily dose of inspiration! 💡"

today = datetime.now().strftime("%B %d, %Y")

# === Metadata ===
title = f"🌟 {quote_text[:80]} | #Shorts"
description = f"""{quote_text}

🎯 Stay inspired every day with a new quote.
💬 What does this quote mean to you? Comment below!

👉 Subscribe for more daily motivation.
#motivation #quotes #shorts #inspiration #positivity #mindset
"""

tags = [
    "shorts", "quotes", "motivationalquotes", "lifelessons", "positivity",
    "selfimprovement", "dailyquotes", "successquotes", "quoteoftheday",
    "mindset", "motivation", "inspiration", "selfgrowth", "wisewords",
    "goodvibes", "wordsoftheday", "selflove", "selfcare", "growthmindset", "viralshorts"
]

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

media = MediaFileUpload(video_file, chunksize=-1, resumable=True, mimetype="video/*")
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
