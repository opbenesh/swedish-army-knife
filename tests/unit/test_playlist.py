

from src.commands.playlist import create_playlist, move_tracks
from tests.fake_spotify import FakeSpotify


def test_move_tracks_batching():
    fake_sp = FakeSpotify()
    fake_sp.add_playlist("src").add_playlist("dst")

    tracks = [f"spotify:track:{i}" for i in range(150)]
    move_tracks(fake_sp, tracks, "src", "dst")

    # 150 tracks → 2 batches of 100/50
    assert fake_sp.call_count("playlist_add_items") == 2
    assert fake_sp.call_count("playlist_remove_all_occurrences_of_items") == 2
    # All tracks ended up in dst
    assert len(fake_sp.playlist_uris("dst")) == 150


def test_move_tracks_empty():
    fake_sp = FakeSpotify()
    move_tracks(fake_sp, [], "src", "dst")
    assert fake_sp.call_count("playlist_add_items") == 0
    assert fake_sp.call_count("playlist_remove_all_occurrences_of_items") == 0


def test_create_playlist():
    fake_sp = FakeSpotify()
    uri = create_playlist(fake_sp, "New Playlist")
    assert uri.startswith("spotify:playlist:")
    # Playlist now exists in fake state
    playlists = {p["name"] for p in fake_sp.current_user_playlists()["items"]}
    assert "New Playlist" in playlists
