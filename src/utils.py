import json
import re
from typing import Optional


def parse_playlist_id(url: str) -> Optional[str]:
    """Extract playlist ID from a Spotify URL. Returns None if the URL is invalid."""
    match = re.search(r'playlist/([a-zA-Z0-9]+)', url)
    return match.group(1) if match else None


def format_track(track: dict, output: str) -> str:
    """Format a track dict for CLI output. output: uri, id, text, or json."""
    if output == "id":
        return track['id']
    elif output == "text":
        artists = ', '.join(a['name'] for a in track['artists'])
        return f"{artists} - {track['name']}"
    elif output == "json":
        artists = ', '.join(a['name'] for a in track['artists'])
        data = {
            "uri": track['uri'],
            "id": track['id'],
            "name": track['name'],
            "artists": artists,
            "release_date": track.get('album', {}).get('release_date'),
        }
        return json.dumps(data)
    else:
        return track['uri']
