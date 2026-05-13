# COA-AutoSolarActivid

Génère des vidéos d'activité solaire (quotidiennes et hebdomadaires), les publie sur YouTube et archive les fichiers produits.

## Table des matières

1. [Structure du projet](#structure-du-projet)
2. [Installation](#installation)
3. [Utilisation locale](#utilisation-locale)
4. [GitHub Actions & YouTube](#github-actions--youtube)
5. [Audio et musique](#audio-et-musique)
6. [Paramètres & personnalisation](#paramètres--personnalisation)
7. [Dépannage](#dépannage)
8. [Sources de données & crédits](#sources-de-données--crédits)
9. [Contribuer](#contribuer)
10. [Licence](#licence)

---

## Structure du projet

```
COA-AutoSolarActivid/
├── scripts/
│   ├── autovideo_daily.py       # Génération vidéo quotidienne
│   ├── autovideo_weekly.py      # Génération vidéo hebdomadaire
│   ├── upload_youtube.py        # Upload YouTube
│   ├── generate_token.py        # Génération du token OAuth
│   └── youtube_manage_playlists.py
├── solar_activity_videos/
│   ├── daily/<YYYY>/<Month>/DDMMYYYY_solar_activity.mp4
│   ├── daily/final_video.mp4    # Alias vers la dernière vidéo
│   ├── weekly/<YYYY>/<Month>/Week n°X (DDMMYYYY-DDMMYYYY).mp4
│   └── weekly/final_video.mp4
├── Protons/
│   ├── daily/                   # JSON GOES quotidiens
│   └── weekly/                  # JSON GOES hebdomadaires
├── .github/workflows/
│   ├── solar_daily.yml
│   └── solar_weekly.yml
├── client_secret.json           # OAuth YouTube (à la racine)
├── token.json                   # Token OAuth (à la racine)
└── requirements.txt
```

> Les dossiers temporaires `SOHO_videos/`, `SOHO_7days/`, `Protons_7days/`, `Neutrons_7days/` sont créés à l'exécution puis nettoyés.

---

## Installation

**Prérequis :** Python ≥ 3.9 (3.11 recommandé), conda ou venv, ffmpeg optionnel.

```bash
git clone https://github.com/Ant1data/COA-AutoSolarActivid.git
cd COA-AutoSolarActivid
pip install -r requirements.txt
```

> **Windows :** Sur certains systèmes, remplacer `opencv-python-headless` par `opencv-python` si un affichage fenêtré est souhaité.

**OAuth YouTube :** `client_secret.json` et `token.json` doivent être présents à la racine. Pour générer le token :

```bash
python scripts/generate_token.py
```

---

## Utilisation locale

### Vidéo quotidienne

```bash
python scripts/autovideo_daily.py
```

Produit :
- `solar_activity_videos/daily/<YYYY>/<Month>/DDMMYYYY_solar_activity.mp4`
- `solar_activity_videos/daily/final_video.mp4` (alias mis à jour)

> La date utilisée est J-1 (UTC). L'audio `track.mp3` est intégré via ffmpeg (fallback : `moviepy`).

### Vidéo hebdomadaire

```bash
python scripts/autovideo_weekly.py
```

Produit :
- `solar_activity_videos/weekly/<YYYY>/<Month>/Week n°X (DDMMYYYY-DDMMYYYY).mp4`
- `solar_activity_videos/weekly/final_video.mp4` (alias mis à jour)

> Pas d'audio intégré pour les vidéos hebdomadaires.

---

## GitHub Actions & YouTube

| Workflow | Déclencheur | Titre YouTube |
|----------|-------------|---------------|
| `solar_daily.yml` | Chaque jour à 00:00 UTC | `Solar Radiation daily — <date J-1>` |
| `solar_weekly.yml` | Chaque lundi à 00:00 UTC | `Solar Radiation weekly — <label semaine>` |

Chaque workflow :
1. Génère la vidéo et met à jour l'alias `final_video.mp4`.
2. Publie sur YouTube Shorts via le secret `YOUTUBE_TOKEN_JSON`.
3. Commit et pousse les nouveaux fichiers (`git pull --rebase` avant push).

**Déclenchement manuel :** onglet Actions > sélectionner le workflow > "Run workflow".

---

## Audio et musique

- La vidéo quotidienne intègre `track.mp3` (méthode : ffmpeg `-c:v copy -c:a aac -shortest`, fallback `moviepy`).
- La description YouTube inclut automatiquement les crédits musicaux :  
  *Travelers — Andrew Prahlow (Outer Wilds OST), ℗ 2019 Annapurna Interactive.*
- **Ne pas utiliser de musique commerciale** pour éviter les blocages YouTube.
- Sources recommandées pour la musique libre :
  - [YouTube Audio Library](https://www.youtube.com/audiolibrary)
  - [Incompetech – Kevin MacLeod](https://incompetech.com/music/royalty-free/)
  - [FreePD](https://freepd.com/)

---

## Paramètres & personnalisation

| Paramètre | Emplacement | Description |
|-----------|-------------|-------------|
| `FPS` | `autovideo_daily.py`, `autovideo_weekly.py` | Images par seconde |
| `DURATION_SEC` | scripts | Durée de la vidéo finale (secondes) |
| `TOTAL_FRAMES` | scripts | Calculé automatiquement (`FPS × DURATION_SEC`) |
| Stations neutrons | `neutron_stations` | Codes NMDB (ex. `MOSC`, `APTY`) |
| Altitudes | dict `altitudes` | Métadonnées pour overlays |
| Énergies protons | extraction regex | Liste `[10, 50, 100, 500]` |
| Rétention quotidienne | fonction purge | Seuil de 14 jours |
| Rétention hebdomadaire | `MAX_WEEKLY_VIDEOS` | Nombre max de vidéos conservées |

---

## Dépannage

| Problème | Cause probable | Solution |
|----------|----------------|----------|
| Pas d'images SOHO | Maintenance serveur / URL changée | Vérifier l'URL `.lst`, réessayer plus tard |
| Timeout NMDB | Latence réseau élevée | Augmenter `timeout` dans `requests.get()` |
| Vidéo noire / vide | Liste d'images vide ou figure Matplotlib vide | Vérifier le filtrage temporel ; logger le nombre d'images |
| MP4 illisible | Codec non supporté | Remuxer : `ffmpeg -i input.mp4 -c copy output.mp4` |
| Erreur SSL (hebdo) | `verify=False` contourné | Fournir les certificats CA ou supprimer `verify=False` |
| JSON manquant | Permission ou dossier absent | Créer `Protons/daily/` et `Protons/weekly/` |
| `cv2` manquant | Dépendances non installées | `pip install -r requirements.txt` |
| `git push` rejeté | Conflit distant | `git pull --rebase` puis recommencer |

---

## Sources de données & crédits

| Source | Données | Lien |
|--------|---------|------|
| SOHO / SDO | Imagerie solaire | https://soho.nascom.nasa.gov |
| NOAA GOES / SWPC | Flux de protons | https://services.swpc.noaa.gov |
| NMDB | Moniteurs à neutrons | https://www.nmdb.eu |

Crédits : ESA & NASA (SOHO/SDO), NOAA NCEI/SWPC (protons), NMDB et stations participantes (neutrons).  
Les crédits apparaissent en overlay sur chaque segment vidéo.

---

## Contribuer

1. Fork du dépôt
2. Créer une branche : `git checkout -b feature/ma-fonctionnalite`
3. Committer : `git commit -m 'Add: ma fonctionnalité'`
4. Pousser : `git push origin feature/ma-fonctionnalite`
5. Ouvrir une Pull Request

Suggestions bienvenues : interpolation de frames, nouvelles stations neutrons, internationalisation des légendes.

---

## Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour les détails.
