from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import json
import os

# Load client credentials and token
with open("client_secret.json", "r") as f:
    content = f.read()
    print(content)  # Debug only, don't use in production
    client_secrets = json.loads(content)

with open("token.json") as f:
    credentials_dict = json.load(f)

from google.oauth2.credentials import Credentials

credentials = Credentials(
    token=credentials_dict['token'],
    refresh_token=credentials_dict['refresh_token'],
    token_uri=client_secrets['installed']['token_uri'],
    client_id=client_secrets['installed']['client_id'],
    client_secret=client_secrets['installed']['client_secret']
)

youtube = build("youtube", "v3", credentials=credentials)

# Set video metadata
video_metadata = {
    "snippet": {
        "title": "🌟 Inspirational Quote #Shorts",
        "description": "Automatically generated inspirational quote video.",
        "tags": ["inspiration", "motivation", "shorts", "quotes"],
        "categoryId": "22"  # People & Blogs
    },
    "status": {
        "privacyStatus": "private"  # Change to "public" after testing
    }
}

# Upload local file
video_file = "short_quote.mp4"
media = MediaFileUpload(video_file, chunksize=-1, resumable=True, mimetype="video/*")

request = youtube.videos().insert(
    part="snippet,status",
    body=video_metadata,
    media_body=media
)

response = None
while response is None:
    status, response = request.next_chunk()
    if status:
        print(f"Uploading... {int(status.progress() * 100)}%")

print("✅ Upload complete!")
print(f"🎥 Video ID: {response['id']}")
