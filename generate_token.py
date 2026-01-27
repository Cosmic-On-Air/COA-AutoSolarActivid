from google_auth_oauthlib.flow import InstalledAppFlow
import os

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
CLIENT_SECRET_FILE = "client_secret.json"

if not os.path.exists(CLIENT_SECRET_FILE):
    raise FileNotFoundError(f"{CLIENT_SECRET_FILE} introuvable.")

flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
creds = flow.run_local_server(port=0)

with open("token.json", "w") as f:
    f.write(creds.to_json())

print("✅ token.json généré avec succès")