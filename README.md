# AutoSolarActivid

Generates solar activity videos (daily and weekly), uploads to YouTube, and archives artifacts in the correct locations.

## Project structure

- `scripts/`: Python scripts (daily/weekly, YouTube upload, token, playlists)
- `solar_activity_videos/`: video outputs and alias `final_video.mp4`
- `Protons/`: NOAA GOES data (proton flux)
- `database/`: caches/images/metadata
- `requirements.txt`: Python dependencies
- `.github/workflows/`: CI for daily/weekly
- `client_secret.json`, `token.json`: YouTube OAuth at project root

## Paths and outputs

- All scripts compute the project root as the parent of `scripts/` and write to the expected top-level folders (never inside `scripts/`).
- The daily pipeline produces a final video with embedded audio and updates the alias `solar_activity_videos/final_video.mp4` directly from the Python script.
- The weekly pipeline remains unchanged script-wise and keeps its weekly alias (audio is not added to weekly by design).

## Embedded audio (daily only)

- `scripts/autovideo_daily.py` embeds the audio track `track.mp3` into the final video.
- Preferred method: ffmpeg (`-c:v copy -c:a aac -shortest`).
- Automatic fallback: `moviepy` when ffmpeg is not available.
- The output name remains the same: referenced by the alias `final_video.mp4`.

## YouTube metadata

- Description: includes music credits (Travelers — Andrew Prahlow, Outer Wilds OST, ℗ 2019 Annapurna Interactive).
- Tags: include `outer wilds`, `Andrew Prahlow`, `Travelers` along with existing tags.
- Upload handled by `scripts/upload_youtube.py`, resolving paths relative to the project root.

## CI (GitHub Actions)

- Workflows: `.github/workflows/solar_daily.yml` and `.github/workflows/solar_weekly.yml` invoke scripts from `scripts/`.
- `actions/checkout@v4` with `fetch-depth: 0` for full history.
- `git pull --rebase` before `git push` to reduce update conflicts.
- YAML alias steps are safeguarded (avoid copying onto itself), but the daily alias is primarily managed by the Python script.

## Local setup and run

Prerequisites: conda and an environment (e.g., `solar`).

1. Activate the environment:
   - Windows PowerShell: activate `solar`, then run scripts.
2. Install dependencies:
   - `pip install -r requirements.txt`
   - Note: `moviepy` is included to ensure audio fallback when ffmpeg is unavailable.
3. Generate the daily video:
   - `python scripts/autovideo_daily.py`
4. Generate the weekly video (without audio changes):
   - `python scripts/autovideo_weekly.py`

## OAuth and secrets

- `client_secret.json` and `token.json` must be present at the project root.
- `scripts/generate_token.py` reads/writes them at the root (do not move them into `scripts/`).

## Troubleshooting

- If `cv2` (OpenCV) is missing: install dependencies via `requirements.txt` (opencv-python-headless recommended in CI).
- If audio is missing, ensure ffmpeg is installed; otherwise `moviepy` should take over.
- If `git push` is rejected, CI uses `git pull --rebase`; do the same locally to resolve conflicts.

## Data sources & credits

- Solar imagery: SOHO (Solar and Heliospheric Observatory) / SDO (Solar Dynamics Observatory) depending on script configuration.
  - Credit: ESA & NASA — please follow each mission’s citation guidelines.
- Proton flux: NOAA GOES (Proton Flux, Space Weather).
  - Credit: NOAA National Centers for Environmental Information (NCEI) / SWPC.
- Ground neutrons: NMDB (Neutron Monitor Database) — stations and aggregations as configured.
  - Credit: NMDB and participating stations.
- YouTube upload & management: Google APIs (YouTube Data API v3) via `google-api-python-client`.
  - Credit: Google Developers — API used for publishing and metadata management.

Music:
- Travelers — Andrew Prahlow (Outer Wilds OST), ℗ 2019 Annapurna Interactive. Credits are automatically added to the YouTube description.

Usage & licensing notes:
- Respect the terms of use for each dataset (NOAA/ESA/NASA/NMDB) and cite sources in descriptions when required.
* Reduced SOHO annotation positioned bottom‑right (better readability).
* Daily / weekly structured JSON saving (`Protons/daily`, `Protons/weekly`).
* Automatic cleanup of old JSON files (daily >14 days, weekly >4 weeks).
* Architecture ready to add more neutron stations (altitude mapping already handled).
* Headless-friendly design for CI and non‑interactive runs (uses `opencv-python-headless`).

## Requirements

* Python 3.11 on GitHub Actions (works locally ≥3.9).
* Core libraries:
  * `requests`, `pandas`, `numpy`, `matplotlib`, `Pillow`
  * `opencv-python-headless`, `scipy`
* See `requirements.txt` for the full list.

### Windows Notes
* Use a virtual environment (`python -m venv .venv`).
* On some systems `opencv-python-headless` may need replacing by `opencv-python` if you want local window display.
* The `mp4v` codec normally writes without FFmpeg; if playback fails, install FFmpeg and remux.

## Installation

Clone the repository:
```bash
git clone https://github.com/Ant1data/AutoSolarActivid.git
cd AutoSolarActivid
```

Install dependencies:
```bash
pip install -r requirements.txt
```

## Local Usage

### Daily generation
```bash
python autovideo_daily.py
```
Produces:
```
solar_activity_videos/daily/<YYYY>/<Month>/DDMMYYYY_solar_activity.mp4
solar_activity_videos/daily/final_video.mp4   # always points to the latest
```
* The daily video and commit message use the date of the previous day (J-1, UTC).

### Weekly generation
```bash
python autovideo_weekly.py
```
Produces:
```
solar_activity_videos/weekly/<YYYY>/<Month>/Week n°X (DDMMYYYY-DDMMYYYY).mp4
solar_activity_videos/weekly/final_video.mp4   # always points to the latest
```

## GitHub Actions & YouTube Upload
Scheduled workflows:
* `solar_daily.yml` – every day at 00:00 UTC + manual dispatch.
* `solar_weekly.yml` – every Monday at 00:00 UTC + manual dispatch.

Each workflow:
- Generates the video(s) and updates the alias `final_video.mp4`.
- Uploads the latest video to YouTube Shorts with a clear title:
  - Daily: `Solar Radiation daily — <date J-1>`
  - Weekly: `Solar Radiation weekly — <week label>`
- Uses a GitHub secret (`YOUTUBE_TOKEN_JSON`) for authentication (see below).
- Commits the new video and JSON with a message reflecting the correct date/period.

Manual trigger: Actions tab > select workflow > "Run workflow".

## Project Structure
```
AutoSolarActivid/
  autovideo_daily.py
  autovideo_weekly.py
  requirements.txt
  solar_activity_videos/
    daily/<YYYY>/<Month>/DDMMYYYY_solar_activity.mp4
    daily/final_video.mp4
    weekly/<YYYY>/<Month>/Week n°X (DDMMYYYY-DDMMYYYY).mp4
    weekly/final_video.mp4
  .github/workflows/
    solar_daily.yml
    solar_weekly.yml
```
Temporary internal folders: `SOHO_videos/`, `SOHO_7days/`, `Protons_7days/`, `Neutrons_7days/`.
Temporary cache used by weekly protons: `Protons/tmp_7days/`.
The historical folder `solar_activity/` may still be created by scripts but is no longer used (replaced by direct downloads).
## Music & Copyright
**Do not use commercial music (e.g. Bag Raiders, etc.) in the generated videos.**
To avoid copyright strikes or blocks on YouTube, use royalty-free or Creative Commons music.

Recommended sources:
- YouTube Audio Library (https://www.youtube.com/audiolibrary)
- Incompetech (Kevin MacLeod) (https://incompetech.com/music/royalty-free/)
- FreePD (https://freepd.com/)

To add music:
- Download a track and place it in `solar_activity_videos/assets/music/`.
- Edit `autovideo_daily.py` or `autovideo_weekly.py` to mix the audio (optionally add a `--music` argument).

## Parameters & Customization
| Parameter | File | Purpose |
|-----------|------|---------|
| `FPS` | `autovideo_daily.py`, `autovideo_weekly.py` | Frames per second (affects smoothness & size). |
| `DURATION_SEC` | scripts | Final clip duration in seconds. |
| `TOTAL_FRAMES` | scripts | Derived (FPS * DURATION_SEC). |
| Neutron stations | `neutron_stations` | Add NMDB codes (e.g. `MOSC`, `APTY`). |
| Altitudes | `altitudes` dict | Metadata for overlays / future analysis. |
| Proton energies | regex extraction | Adjust list `[10,50,100,500]`. |
| Daily retention | purge function | Change 14‑day threshold. |
| Weekly retention | `MAX_WEEKLY_VIDEOS` | Limit number of stored weekly videos. |

## Troubleshooting
| Issue | Likely cause | Quick fix |
|------|--------------|-----------|
| No SOHO images | Server maintenance / path changed | Check `.lst` URL, retry later. |
| NMDB timeout | High network latency | Increase `requests.get(..., timeout=30)`. |
| Empty / black video | Empty image list or Matplotlib figure | Verify time filtering; log image count. |
| Unplayable MP4 | Codec unsupported by player | Convert via `ffmpeg -i input.mp4 -c copy output.mp4`. |
| SSL error (weekly) | Using `verify=False` workaround | Provide CA certs or remove `verify=False`. |
| Missing JSON file | Write permission / missing dir | Ensure `Protons/daily|weekly` hierarchy exists. |

## Naming & Retention
* Video length: 15 s – 60 FPS (900 frames).
* Automatic purge > 14 days (daily & weekly).
* Configurable weekly retention (`MAX_WEEKLY_VIDEOS`).
* Latest video always available as `final_video.mp4` (daily & weekly).

## Data Sources & Credits
* SOHO LASCO C2 – © NASA/ESA: https://soho.nascom.nasa.gov
* GOES Proton Flux – NOAA SWPC: https://services.swpc.noaa.gov
* NMDB Neutron Monitor Database: https://www.nmdb.eu

Thanks to the providers of public data. Attribution overlays appear on each segment.
YouTube upload is automated via GitHub Actions and uses a secure OAuth token (see repository secrets).

## Contributing
Suggestions welcome: performance optimizations (e.g. frame interpolation), adding neutron stations, caption internationalization.
1. Fork
2. Branch (`git checkout -b feature/my-feature`)
3. Commit (`git commit -m 'Add: my feature'`)
4. Push (`git push origin feature/my-feature`)
5. Open a Pull Request

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.