from src.commands.playlist import (
    LIKED_SENTINEL,
    resolve_or_create_playlist_id,
    resolve_playlist_id,
)
from tests.fake_spotify import FakeSpotify

_REAL_ID = "A" * 22  # 22-char base62 — passes straight through


def test_resolve_passes_through_22char_id():
    fake_sp = FakeSpotify()
    assert resolve_playlist_id(fake_sp, _REAL_ID) == _REAL_ID


def test_resolve_passes_through_liked():
    fake_sp = FakeSpotify()
    assert resolve_playlist_id(fake_sp, LIKED_SENTINEL) == LIKED_SENTINEL


def test_resolve_finds_by_name():
    fake_sp = FakeSpotify()
    fake_sp.add_playlist("actual_id", name="My Playlist")
    assert resolve_playlist_id(fake_sp, "My Playlist") == "actual_id"


def test_resolve_falls_back_for_unknown():
    fake_sp = FakeSpotify()
    # Not a known name, not a 22-char ID → returned as-is
    assert resolve_playlist_id(fake_sp, "src_id") == "src_id"


def test_resolve_or_create_passes_through_22char_id():
    fake_sp = FakeSpotify()
    result, created = resolve_or_create_playlist_id(fake_sp, _REAL_ID)
    assert result == _REAL_ID
    assert created is False


def test_resolve_or_create_finds_existing():
    fake_sp = FakeSpotify()
    fake_sp.add_playlist("existing_id", name="My Playlist")
    result, created = resolve_or_create_playlist_id(fake_sp, "My Playlist")
    assert result == "existing_id"
    assert created is False


def test_resolve_or_create_creates_new():
    fake_sp = FakeSpotify()
    result, created = resolve_or_create_playlist_id(fake_sp, "Brand New")
    assert created is True
    # FakeSpotify derives ID from name
    assert result == "pl_brand_new"
    # Playlist now exists
    assert "Brand New" in {p["name"] for p in fake_sp.current_user_playlists()["items"]}
