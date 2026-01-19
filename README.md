# 🇸🇪🔪 Swedish Army Knife

> A personal CLI toolkit for Spotify playlist automation.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## ✨ Features

- **Move Tracks** — Bulk move tracks between playlists with a single command
- **Efficient** — Batches API calls (100 tracks per request) to stay fast and avoid rate limits
- **Secure** — Pre-commit hooks detect secrets before they're committed

## 🚀 Quick Start

### 1. Clone & Setup

```bash
git clone https://github.com/opbenesh/swedish-army-knife.git
cd swedish-army-knife
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Spotify Credentials

1. Create a [Spotify Developer App](https://developer.spotify.com/dashboard)
2. Add `http://localhost:8888/callback` as a Redirect URI in your app settings
3. Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
# Edit .env with your SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET
```

### 3. Verify Connection

```bash
python -m src.main status
```

On first run, a browser window will open for Spotify OAuth authorization.

## 📖 Usage

### Move Tracks Between Playlists

Create a text file with track URIs (one per line):

```text
spotify:track:4iV5W9uYEdYUVa79Axb7Rh
spotify:track:1301WleyT98MSxVHPZCA6M
```

Then run:

```bash
python -m src.main playlist move --file tracks.txt --from SOURCE_PLAYLIST_ID --to DEST_PLAYLIST_ID
```

## 🧪 Development

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests (unit only)
pytest tests/unit/

# Run all tests including live API tests
RUN_LIVE_TESTS=true pytest tests/
```

## 📁 Project Structure

```
src/
├── main.py            # CLI entry point
├── spotify_client.py  # OAuth wrapper
├── config.py          # Environment loader
└── commands/
    └── playlist.py    # Playlist operations
```

## 📄 License

MIT
