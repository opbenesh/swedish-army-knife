"""In-memory Spotify client for testing.

Use FakeSpotify.add_playlist() to seed state, then inspect it after operations
instead of asserting on mock call args.
"""
from __future__ import annotations

from typing import Optional


def _make_track(uri: str, name: str = "", artists: list | None = None) -> dict:
    track_id = uri.split(":")[-1] if ":" in uri else uri
    return {
        "id": track_id,
        "uri": uri if uri.startswith("spotify:track:") else f"spotify:track:{uri}",
        "name": name or f"Track {track_id}",
        "artists": artists or [{"name": "Test Artist"}],
        "album": {"release_date": "2020-01-01"},
    }


class FakeSpotify:
    def __init__(self) -> None:
        self._playlists: dict[str, dict] = {}
        self._user: dict = {"id": "testuser", "display_name": "Test User"}
        self._search_results: dict[str, dict] = {}
        self._default_search_result: Optional[dict] = None
        self.calls: list[tuple] = []

    # ── Seed helpers ────────────────────────────────────────────────────────

    def add_playlist(
        self,
        playlist_id: str,
        name: str = "Test Playlist",
        tracks: list[dict | str] | None = None,
    ) -> "FakeSpotify":
        """Seed a playlist. tracks should be full track dicts or bare URIs."""
        normalised = []
        for t in (tracks or []):
            if isinstance(t, str):
                normalised.append(_make_track(t))
            else:
                normalised.append(t)
        self._playlists[playlist_id] = {"id": playlist_id, "name": name, "tracks": normalised}
        return self

    def set_search_result(self, query: str, track: dict) -> "FakeSpotify":
        self._search_results[query] = track
        return self

    def set_default_search_result(self, track: dict) -> "FakeSpotify":
        self._default_search_result = track
        return self

    def playlist_uris(self, playlist_id: str) -> list[str]:
        """Convenience: return just the URIs in a playlist."""
        return [t["uri"] for t in self._playlists.get(playlist_id, {}).get("tracks", [])]

    def call_count(self, method: str) -> int:
        return sum(1 for c in self.calls if c[0] == method)

    # ── spotipy interface ────────────────────────────────────────────────────

    def current_user(self) -> dict:
        return self._user

    def current_user_playlists(self) -> dict:
        items = [{"id": p["id"], "name": p["name"]} for p in self._playlists.values()]
        return {"items": items, "next": None}

    def playlist_tracks(self, playlist_id: str, **kwargs) -> dict:
        tracks = self._playlists.get(playlist_id, {}).get("tracks", [])
        return {"items": [{"track": t} for t in tracks], "next": None}

    def next(self, result: dict) -> None:
        return None

    def playlist_add_items(self, playlist_id: str, uris: list[str]) -> None:
        self.calls.append(("playlist_add_items", playlist_id, list(uris)))
        if playlist_id not in self._playlists:
            self._playlists[playlist_id] = {"id": playlist_id, "name": "Unknown", "tracks": []}
        for uri in uris:
            self._playlists[playlist_id]["tracks"].append(_make_track(uri))

    def playlist_remove_all_occurrences_of_items(self, playlist_id: str, uris: list[str]) -> None:
        self.calls.append(("playlist_remove_all_occurrences_of_items", playlist_id, list(uris)))
        uri_set = set(uris)
        if playlist_id in self._playlists:
            self._playlists[playlist_id]["tracks"] = [
                t for t in self._playlists[playlist_id]["tracks"] if t["uri"] not in uri_set
            ]

    def user_playlist_create(self, user_id: str, name: str) -> dict:
        playlist_id = f"pl_{name.lower().replace(' ', '_')}"
        self._playlists[playlist_id] = {"id": playlist_id, "name": name, "tracks": []}
        return {"id": playlist_id, "uri": f"spotify:playlist:{playlist_id}"}

    def search(self, q: str, type: str = "track", limit: int = 1) -> dict:
        self.calls.append(("search", q))
        if q in self._search_results:
            return {"tracks": {"items": [self._search_results[q]]}}
        if self._default_search_result is not None:
            return {"tracks": {"items": [self._default_search_result]}}
        return {"tracks": {"items": []}}
