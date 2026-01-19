# Agent Environment Notes

**Last Updated:** 2026-01-19
**Project:** Spotify Swiss Army Knife (CLI)

This document provides guidance for AI agents working on the Spotify Swiss Army Knife CLI project.

---

## Important Guidelines

### Development Workflow
- **IMPORTANT - TDD Required**: Write tests first (e.g., using `pytest` and `unittest.mock` for Spotify API calls), verify they fail, implement the solution, verify tests pass. Never assume your solution works without proof.
- **CRITICAL - Bug Fix Workflow**: When you discover a bug:
  1. **Add a test case** that reproduces the bug.
  2. **Run the test** and verify it fails.
  3. **Fix the bug** in the source code.
  4. **Run the test again** and verify it passes.
- **Documentation**: Maintain `README.md` and `task.md` recursively as features are added.

### Coding Guidelines
- **SOLID Principles**:
    - **Single Responsibility**: Keep CLI commands (`src/commands/`) separate from API client logic (`src/spotify_client.py`).
    - **Open-Closed**: Design the CLI to be extendable with new commands without modifying the core auth logic.
- **DRY (Don't Repeat Yourself)**: Extract common track/playlist parsing logic into a utility module if reused across commands.
- **Type Hints**: Use Python type hints for all function signatures to improve maintainability and local agent reasoning.
- **Error Handling**: 
    - Use specific exceptions (e.g., `spotipy.exceptions.SpotifyException`).
    - Provide user-friendly error messages for CLI users (e.g., "Playlist not found") instead of raw tracebacks.
- **API Efficiency**:
    - **CRITICAL**: Minimize Spotify API calls. 
    - Batch operations wherever possible (e.g., add up to 100 tracks per call).
    - Cache metadata (like user ID or playlist IDs) if they won't change during the execution of a single command.
- **Testing Strategy**:
    - **Unit Tests**: Focus on business logic (e.g., track list parsing, ID extraction) using `pytest`.
    - **Mocking**: Use `pytest-mock` or `unittest.mock` to simulate the Spotify API. This avoids hitting rate limits and requires no credentials for CI.
    - **Integration Tests**: Minimal set of tests that hit the *actual* Spotify API (requires `.env` with valid keys). These should be skipped unless an environment variable like `RUN_LIVE_TESTS=true` is set.
    - **Regression**: Any fixed bug must have a corresponding test case to prevent it from returning.

### Unix Philosophy (CLI Design)
- **Small Tools**: Each command should do one thing well (e.g., `move-tracks`).
- **Input/Output**: 
    - Support reading track IDs/URIs from files or `stdin`.
    - Use `stdout` for the primary results (e.g., list of IDs) and `stderr` for logging/progress.
- **Piping**: Design output format (like plain text or JSON) so it can be piped into other tools.

### Security & Personalization
- **Secrets**: NEVER commit `.env`. Ensure it's in `.gitignore`.
- **Environment**: All Spotify credentials must be loaded via `python-dotenv` from the `.env` file.

---

## Project Overview

This is a **Spotify automation CLI tool** ("Swedish Army Knife") for personal use. It allows the user to perform daily routine tasks involving Spotify playlists and tracks.

### Architecture

**Core Philosophy:**
- CLI-based workflow (built with `typer`)
- Direct API interaction (via `spotipy`)
- Local configuration (`.env`)

**Key Components:**
```
src/
├── main.py            - CLI entry point
├── spotify_client.py  - SpotifyAuth and Client wrapper
├── commands/
│   └── playlist.py    - Playlist management logic
└── config.py          - Configuration management
```

---

## Key Workflows

### 1. Source Control
- **Main Branch**: `main`
- **Secrets**: NEVER commit `.env` files. Ensure `venv` is also ignored.

### 2. Authentication
- Uses `spotipy.oauth2.SpotifyOAuth`.
- Requires `SPOTIPY_CLIENT_ID`, `SPOTIPY_CLIENT_SECRET`, `SPOTIPY_REDIRECT_URI` in `.env`.
- The first run will trigger a browser window for OAuth approval; cached tokens go to `.cache`.

---

## Tools & Dependencies

### Python
- Python 3.9+
- `spotipy`: Official-ish Python library for Spotify Web API.
- `typer`: Modern library for building CLI applications.
- `python-dotenv`: Environment variable management.
- `rich`: For beautiful terminal formatting and progress bars.

### Testing
- `pytest`: Preferred test runner.
- `pytest-mock`: For mocking the Spotify API in unit tests.