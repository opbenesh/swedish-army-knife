# 🇸🇪🔪 Swedish Army Knife

> A personal CLI toolkit for Spotify playlist automation.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## ✨ Features

- **List Tracks** — Export playlist contents as `Artist - Title` lines
- **Search Tracks** — Find Spotify URIs from `Artist - Title` input
- **Add Tracks** — Batch add tracks to playlists
- **Move Tracks** — Bulk move tracks between playlists
- **Pipeable** — Unix-friendly: pipe commands together for powerful workflows
- **Efficient** — Batches API calls (100 tracks per request) to avoid rate limits

## 🚀 Quick Start

### 1. Clone & Setup

```bash
git clone https://github.com/opbenesh/swedish-army-knife.git
cd swedish-army-knife
python3 -m venv venv
source venv/bin/activate
pip install -e .
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
sak status
```

On first run, a browser window will open for Spotify OAuth authorization.

## 📖 Usage

### Create a Playlist

```bash
sak playlist create --name "My New Playlist"
# Output: spotify:playlist:NEW_ID
```

### List Tracks from a Playlist

```bash
# Using playlist URL
sak playlist list --url "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"

# Using playlist ID
sak playlist list --id 37i9dQZF1DXcBWIGoYBM5M
```

Output (one track per line):
```
Artist Name - Track Title
Another Artist - Another Track
```

### Search for Track URIs

Pipe `Artist - Title` lines to get Spotify URIs:

```bash
echo "Daft Punk - Get Lucky" | sak playlist search
# Output: spotify:track:2Foc5Q5nqNiosCNqttzHof
```

#### Search with Metadata (JSON)

Use `--format json` to get detailed track metadata including release dates:

```bash
echo "Daft Punk - Get Lucky" | sak playlist search --format json
# Output: {"uri": "spotify:track:2Foc...", "release_date": "2013-05-17", ...}
```

### Add Tracks to a Playlist

```bash
# From a file
sak playlist add --file tracks.txt --id DEST_ID

# Direct piping: List -> Search -> Add
sak playlist list --id SOURCE_ID | sak playlist search | sak playlist add --id DEST_ID
```

### Move Tracks Between Playlists

```bash
# From a file
sak playlist move --file tracks.txt --from SOURCE_ID --to DEST_ID

# Or pipe URIs directly
sak playlist list --id SOURCE_ID | sak playlist search | sak playlist move --from SOURCE_ID --to DEST_ID
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
