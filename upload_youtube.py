import os
import json
import argparse
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

# ============================================================
# 1. Arguments CLI
# ============================================================

parser = argparse.ArgumentParser(description="Upload video to YouTube Shorts")
parser.add_argument("--video", help="Path to video file")
parser.add_argument("--type", choices=["DAILY", "WEEKLY"], help="COA type")
parser.add_argument("--label", help="Date / week label")
args = parser.parse_args()

# ============================================================
# 2. OAuth token (ENV ONLY, volontairement)
# ============================================================

raw_token = os.environ.get("YOUTUBE_TOKEN_JSON") or os.environ.get("YOUTUBE_TOKEN")
if not raw_token:
    raise RuntimeError("Missing YOUTUBE_TOKEN_JSON in environment")

try:
    token_info = json.loads(raw_token)
except json.JSONDecodeError as e:
    raise RuntimeError("Invalid JSON in YOUTUBE_TOKEN_JSON") from e

creds = Credentials.from_authorized_user_info(
    token_info,
    scopes=["https://www.googleapis.com/auth/youtube.upload"],
)

youtube = build("youtube", "v3", credentials=creds)

# ============================================================
# 3. Résolution des paramètres (CLI > ENV > défaut)
# ============================================================

video_path = (
    args.video
    or os.environ.get("YOUTUBE_VIDEO_PATH")
)

if not video_path or not os.path.exists(video_path):
    raise RuntimeError(f"Video file not found: {video_path}")

coa_type = (
    args.type
    or os.environ.get("COA_TYPE")
    or "DAILY"
).upper()

label = (
    args.label
    or os.environ.get("COA_DATE_LABEL")
    or datetime.utcnow().strftime("%Y-%m-%d")
)

# ============================================================
# 4. Métadonnées YouTube
# ============================================================

title = (
    f"COA {coa_type} {label} "
    "#cosmic #radiation #airplane #spaceweather #solarflare"
)

description = (
    "Data Sources & Credits\n"
    "SOHO LASCO C2 – © NASA/ESA: https://soho.nascom.nasa.gov\n"
    "GOES Proton Flux – NOAA SWPC: https://services.swpc.noaa.gov\n"
    "NMDB Neutron Monitor Database: https://www.nmdb.eu\n\n"
    "Thanks to the providers of public data.\n"
    "Attribution overlays appear on each segment."
)

tags = [
    "cosmic", "radiation", "airplane",
    "spaceweather", "solarflare",
    "cosmic on air", "COA"
]

# ============================================================
# 5. Upload
# ============================================================

request = youtube.videos().insert(
    part="snippet,status",
    body={
        "snippet": {
            "title": title[:100],
            "description": description,
            "tags": tags,
            "categoryId": "28",
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False,
        },
    },
    media_body=MediaFileUpload(video_path, resumable=True),
)

print(f"📤 Upload YouTube ({coa_type}) : {video_path}")
response = request.execute()

video_id = response.get("id")
if not video_id:
    raise RuntimeError("Upload failed: no video ID returned")

print(f"✅ Upload terminé : https://www.youtube.com/shorts/{video_id}")
