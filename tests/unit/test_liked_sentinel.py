from src.commands.playlist import (
    LIKED_SENTINEL,
    get_liked_track_uris,
    move_tracks,
    remove_liked_tracks,
)
from tests.fake_spotify import FakeSpotify


def test_list_liked_track_uris():
    fake_sp = FakeSpotify()
    uris = [f"spotify:track:{i}" for i in range(5)]
    fake_sp.add_saved_tracks(uris)

    result = get_liked_track_uris(fake_sp)
    assert result == set(uris)


def test_list_liked_empty():
    fake_sp = FakeSpotify()
    assert get_liked_track_uris(fake_sp) == set()


def test_remove_liked_tracks():
    fake_sp = FakeSpotify()
    uris = [f"spotify:track:{i}" for i in range(5)]
    fake_sp.add_saved_tracks(uris)

    remove_liked_tracks(fake_sp, uris)
    assert fake_sp.saved_uris() == []


def test_remove_liked_tracks_batches():
    fake_sp = FakeSpotify()
    uris = [f"spotify:track:{i}" for i in range(110)]
    fake_sp.add_saved_tracks(uris)

    remove_liked_tracks(fake_sp, uris)
    # 110 tracks → 3 batches of 50/50/10
    assert fake_sp.call_count("current_user_saved_tracks_delete") == 3
    assert fake_sp.saved_uris() == []


def test_move_from_liked_removes_from_saved():
    fake_sp = FakeSpotify()
    uris = [f"spotify:track:{i}" for i in range(3)]
    fake_sp.add_saved_tracks(uris)
    fake_sp.add_playlist("dest")

    move_tracks(fake_sp, uris, LIKED_SENTINEL, "dest")

    assert fake_sp.saved_uris() == []
    assert set(fake_sp.playlist_uris("dest")) == set(uris)


def test_move_from_liked_batches():
    fake_sp = FakeSpotify()
    uris = [f"spotify:track:{i}" for i in range(110)]
    fake_sp.add_saved_tracks(uris)
    fake_sp.add_playlist("dest")

    move_tracks(fake_sp, uris, LIKED_SENTINEL, "dest")

    # 110 tracks → 2 batches of 100/10 (BATCH_SIZE=100)
    assert fake_sp.call_count("current_user_saved_tracks_delete") == 2
    assert fake_sp.call_count("playlist_remove_all_occurrences_of_items") == 0
    assert len(fake_sp.playlist_uris("dest")) == 110


def test_move_from_liked_strict_filters_to_saved():
    fake_sp = FakeSpotify()
    saved = [f"spotify:track:{i}" for i in range(3)]
    extra = ["spotify:track:not_liked"]
    fake_sp.add_saved_tracks(saved)
    fake_sp.add_playlist("dest")

    move_tracks(fake_sp, saved + extra, LIKED_SENTINEL, "dest", strict=True)

    # Only the 3 saved tracks should move; the extra one is skipped
    assert set(fake_sp.playlist_uris("dest")) == set(saved)
    assert fake_sp.saved_uris() == []
