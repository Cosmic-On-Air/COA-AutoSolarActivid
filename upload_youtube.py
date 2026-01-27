import os
import json
import re
from datetime import date
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

# Fallbacks pour éviter KeyError
VIDEO_PATH = os.environ.get("YOUTUBE_VIDEO_PATH", "solar_activity_videos/daily/final_video.mp4")
COA_TYPE = os.environ.get("COA_TYPE", "DAILY")  # DAILY ou WEEKLY
DATE_LABEL = os.environ.get("COA_DATE_LABEL", date.today().isoformat())

# Sanitize helper pour enlever les caractères de contrôle
_def_ctrl_re = re.compile(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]')

def sanitize_json_string(s: str) -> str:
    return _def_ctrl_re.sub('', s)

_raw_token = os.environ.get("YOUTUBE_TOKEN_JSON") or os.environ.get("YOUTUBE_TOKEN")
if not _raw_token:
    raise RuntimeError("Missing YOUTUBE_TOKEN_JSON/YOUTUBE_TOKEN in environment")

token_info = json.loads(sanitize_json_string(_raw_token))
creds = Credentials.from_authorized_user_info(token_info, SCOPES)
youtube = build("youtube", "v3", credentials=creds)

TITLE = (
    f"COA {COA_TYPE.capitalize()} – {DATE_LABEL}  "
    "#cosmic #radiation #airplane #spaceweather #solarflare"
)

DESCRIPTION = f"""Cosmic on Air – Automated Space Weather Report

Data Sources & Credits
SOHO LASCO C2 – © NASA/ESA
https://soho.nascom.nasa.gov

GOES Proton Flux – NOAA SWPC
https://services.swpc.noaa.gov

NMDB Neutron Monitor Database
https://www.nmdb.eu

Thanks to the providers of public data.
Attribution overlays appear on each segment.

COA_TYPE={COA_TYPE}
COA_GENERATED={date.today().isoformat()}
"""

request = youtube.videos().insert(
    part="snippet,status",
    body={
        "snippet": {
            "title": TITLE,
            "description": DESCRIPTION,
            "categoryId": "28",
        },
        "status": {
            "privacyStatus": "public"
        },
    },
    media_body=MediaFileUpload(VIDEO_PATH, resumable=True),
)

response = request.execute()
print("UPLOAD_OK", response["id"])
