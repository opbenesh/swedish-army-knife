# 🇸🇪🔪 Swedish Army Knife

> A personal CLI toolkit for Spotify playlist automation.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI](https://github.com/opbenesh/swedish-army-knife/actions/workflows/ci.yml/badge.svg)](https://github.com/opbenesh/swedish-army-knife/actions/workflows/ci.yml)

## ✨ Features

- **List Tracks** — Export playlist contents as `Artist - Title` lines
- **Search Tracks** — Find Spotify URIs from `Artist - Title` input
- **Add Tracks** — Batch add tracks to playlists
- **Move Tracks** — Bulk move tracks between playlists
- **Pipeable** — Unix-friendly: pipe commands together for powerful workflows
- **Efficient** — Batches API calls (100 tracks per request) to avoid rate limits

## 🚀 Quick Start

### 1. Clone & Setup

Requires [uv](https://docs.astral.sh/uv/getting-started/installation/).

```bash
git clone https://github.com/opbenesh/swedish-army-knife.git
cd swedish-army-knife
uv sync
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
uv run sak status
```

On first run, a browser window will open for Spotify OAuth authorization.

## 📖 Usage

### Create a Playlist

```bash
sak playlist create --name "My New Playlist"
# Output: spotify:playlist:NEW_ID
```

### Find a Playlist ID by Name

```bash
sak playlist find "My Playlist"
# Output: 37i9dQZF1DXcBWIGoYBM5M
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

#### Search within a Playlist

You can also restrict the search to a specific playlist using the `--in-playlist` flag. This uses fuzzy matching locally, which is more efficient for large lists and prevents finding tracks outside your source playlist:

```bash
cat tracklist.txt | sak playlist search --in-playlist <playlist_id>
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

# Use --strict to only move tracks that actually exist in the source playlist
sak playlist move --file tracks.txt --from SOURCE_ID --to DEST_ID --strict

# Or pipe URIs directly
sak playlist list --id SOURCE_ID | sak playlist search | sak playlist move --from SOURCE_ID --to DEST_ID
```

## 🧪 Development

```bash
# Install dev dependencies
uv sync --group dev

# Run tests
uv run pytest

# Lint
uv run ruff check .

# Run live API tests (requires valid .env credentials)
RUN_LIVE_TESTS=true uv run pytest
```

## 📁 Project Structure

```
src/
├── main.py            # CLI entry point
├── spotify_client.py  # OAuth wrapper
├── config.py          # Environment loader
├── utils.py           # Shared helpers (URL parsing, track formatting)
└── commands/
    └── playlist.py    # Playlist operations

tests/
├── fake_spotify.py    # In-memory Spotify fake for testing
├── conftest.py        # Shared fixtures
└── unit/              # Unit tests
```

## 📄 License

MIT
