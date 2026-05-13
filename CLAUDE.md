Spotify automation CLI. Entry point: `src/main.py`. Deps: uv.

## Commands
- Run: `uv run sak --help`
- Test: `uv run pytest`
- Lint: `uv run ruff check .` | `uv run ruff format .`
- Type check: `uv run ty check`

## Auth
SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI in `.env`.
First run opens a browser for OAuth; token cached in `.cache`.

## Testing
Bug workflow: add failing test first, confirm it fails, fix, confirm it passes.
Use FakeSpotify (`tests/fake_spotify.py`) for state-based tests; MagicMock only for error paths.
