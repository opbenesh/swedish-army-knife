from src.commands.playlist import move_tracks
from tests.fake_spotify import FakeSpotify


def test_move_tracks_strict_filters_missing():
    """Strict mode: only tracks present in source are moved."""
    fake_sp = FakeSpotify()
    fake_sp.add_playlist("src", tracks=["spotify:track:1", "spotify:track:2"])
    fake_sp.add_playlist("dst")

    move_tracks(fake_sp, ["spotify:track:2", "spotify:track:3"], "src", "dst", strict=True)

    assert fake_sp.playlist_uris("dst") == ["spotify:track:2"]
    assert "spotify:track:1" in fake_sp.playlist_uris("src")
    assert "spotify:track:2" not in fake_sp.playlist_uris("src")


def test_move_tracks_non_strict_moves_all():
    """Non-strict mode: all provided tracks are moved unconditionally."""
    fake_sp = FakeSpotify()
    fake_sp.add_playlist("src")
    fake_sp.add_playlist("dst")

    move_tracks(fake_sp, ["spotify:track:2", "spotify:track:3"], "src", "dst", strict=False)

    assert set(fake_sp.playlist_uris("dst")) == {"spotify:track:2", "spotify:track:3"}


def test_move_tracks_strict_normalises_ids():
    """Strict mode normalises bare IDs to URIs for comparison."""
    fake_sp = FakeSpotify()
    fake_sp.add_playlist("src", tracks=["spotify:track:track1", "spotify:track:track2"])
    fake_sp.add_playlist("dst")

    # Input uses bare IDs (no spotify:track: prefix)
    move_tracks(fake_sp, ["track2", "track3"], "src", "dst", strict=True)

    # Only track2 was in source; track3 was not
    dst_uris = fake_sp.playlist_uris("dst")
    assert len(dst_uris) == 1
    # track2 in destination (as bare id since that's what was passed)
    assert any("track2" in u for u in dst_uris)
