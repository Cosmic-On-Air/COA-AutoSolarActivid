import os
import json
from datetime import date
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

VIDEO_PATH = os.environ["YOUTUBE_VIDEO_PATH"]
COA_TYPE = os.environ["COA_TYPE"]  # DAILY ou WEEKLY
DATE_LABEL = os.environ["COA_DATE_LABEL"]

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

token_info = json.loads(os.environ["YOUTUBE_TOKEN"])
creds = Credentials.from_authorized_user_info(token_info, SCOPES)
youtube = build("youtube", "v3", credentials=creds)

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
