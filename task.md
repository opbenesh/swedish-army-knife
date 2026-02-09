# Task Tracking

- [x] Implement `sak playlist create --name "NAME"` command
    - [x] Add `create_playlist` to `src/commands/playlist.py`
    - [x] Add `create` command to `src/main.py`
    - [x] Write unit tests for `create_playlist` and the CLI command
- [x] Implement `sak playlist search --format json` command
    - [x] Update `search` command in `src/main.py` to support `--format json`
    - [x] Ensure `release_date` is included in the JSON output
    - [x] Write unit tests for JSON output format
- [x] Update `README.md` with new features
- [x] Complete pre-commit steps

## Playlist Management
- [x] `sak status` - Check connection status
- [x] `sak playlist list` - List tracks from a playlist
- [x] `sak playlist search` - Search for track URIs from text input
    - [x] Support `--in-playlist` for fuzzy matching
    - [x] Support `--format json` for metadata
- [x] `sak playlist add` - Add tracks to a playlist
- [x] `sak playlist move` - Move tracks between playlists
- [x] `sak playlist find` - Look up a playlist ID by its name

## Internal Improvements
- [x] Refactor search logic to `src/commands/playlist.py`
- [x] Integrate `rapidfuzz` for fuzzy matching
