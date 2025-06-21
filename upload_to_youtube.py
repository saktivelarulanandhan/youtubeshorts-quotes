import os
import json
import google.auth
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Scopes required for uploading video
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def authenticate_youtube():
    creds = None

    if os.path.exists("token.json"):
        with open("token.json", "r") as token:
            creds = google.oauth2.credentials.Credentials.from_authorized_user_info(json.load(token), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return build("youtube", "v3", credentials=creds)

def upload_video(file_path, title, description, tags=None, categoryId="22", privacyStatus="private"):
    youtube = authenticate_youtube()

    request_body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags or [],
            "categoryId": categoryId  # "22" is for People & Blogs
        },
        "status": {
            "privacyStatus": privacyStatus,
            "selfDeclaredMadeForKids": False
        }
    }

    media = MediaFileUpload(file_path, chunksize=-1, resumable=True, mimetype="video/*")

    print("📤 Uploading to YouTube...")
    request = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=media
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"⏳ Upload progress: {int(status.progress() * 100)}%")

    print("✅ Upload complete.")
    print("🎥 Video ID:", response["id"])

if __name__ == "__main__":
    upload_video(
        file_path="short_quote.mp4",
        title="🌟 Inspiring Quote of the Day #shorts",
        description="A daily dose of inspiration! #motivationalquotes #shorts",
        tags=["inspiration", "quotes", "shorts"],
        privacyStatus="public"  # or "private"/"unlisted"
    )
