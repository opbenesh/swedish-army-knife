import os
import pytest
from src.spotify_client import get_spotify

# Only run if explicitly enabled
pytestmark = pytest.mark.skipif(
    os.getenv("RUN_LIVE_TESTS") != "true",
    reason="RUN_LIVE_TESTS=true not set"
)

def test_spotify_connection_live():
    """Verify we can connect to Spotify and get current user info."""
    sp = get_spotify()
    user = sp.current_user()
    assert user is not None
    assert "id" in user
    print(f"Connected as: {user['display_name']}")

def test_spotify_playlist_list_live():
    """Verify we can fetch user playlists."""
    sp = get_spotify()
    playlists = sp.current_user_playlists(limit=1)
    assert "items" in playlists
