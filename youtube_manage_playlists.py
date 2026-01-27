import json
import os
import re
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

SCOPES = ["https://www.googleapis.com/auth/youtube"]

# Sanitize helper to remove control chars
_def_ctrl_re = re.compile(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]')

def sanitize_json_string(s: str) -> str:
    return _def_ctrl_re.sub('', s)

# Read token from env with fallback and sanitize
_raw_token = os.environ.get("YOUTUBE_TOKEN_JSON") or os.environ.get("YOUTUBE_TOKEN")
if not _raw_token:
    raise RuntimeError("Missing YOUTUBE_TOKEN_JSON/YOUTUBE_TOKEN in environment")

_token_info = json.loads(sanitize_json_string(_raw_token))
creds = Credentials.from_authorized_user_info(_token_info, SCOPES)
youtube = build("youtube", "v3", credentials=creds)

PLAYLISTS = {
    "DAILY": ("COA – Daily (last 30 days)", 30),
    "WEEKLY": ("COA – Weekly (last 4 weeks)", 28),
}

def get_or_create_playlist(title):
    pl = youtube.playlists().list(part="id,snippet", mine=True, maxResults=50).execute()
    for p in pl.get("items", []):
        if p["snippet"]["title"] == title:
            return p["id"]

    res = youtube.playlists().insert(
        part="snippet,status",
        body={
            "snippet": {"title": title},
            "status": {"privacyStatus": "public"},
        },
    ).execute()
    return res["id"]

playlist_ids = {
    k: get_or_create_playlist(v[0]) for k, v in PLAYLISTS.items()
}

videos = youtube.search().list(
    part="id,snippet",
    forMine=True,
    type="video",
    maxResults=50,
).execute()

now = datetime.utcnow()

for v in videos.get("items", []):
    vid = v["id"]["videoId"]
    desc = v["snippet"]["description"]

    if "COA_TYPE=" not in desc:
        continue

    coa_type = "DAILY" if "COA_TYPE=DAILY" in desc else "WEEKLY"
    published = datetime.strptime(
        v["snippet"]["publishedAt"], "%Y-%m-%dT%H:%M:%SZ"
    )
    age_days = (now - published).days
    max_age = PLAYLISTS[coa_type][1]

    if age_days <= max_age:
        youtube.playlistItems().insert(
            part="snippet",
            body={
                "snippet": {
                    "playlistId": playlist_ids[coa_type],
                    "resourceId": {
                        "kind": "youtube#video",
                        "videoId": vid,
                    },
                }
            },
        ).execute()
