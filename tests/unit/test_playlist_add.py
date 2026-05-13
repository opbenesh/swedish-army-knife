from unittest.mock import patch

from typer.testing import CliRunner

from src.commands.playlist import add_tracks
from src.main import app
from tests.fake_spotify import FakeSpotify

runner = CliRunner()


def test_add_tracks_logic_batching():
    """add_tracks batches 250 tracks into 3 API calls (100, 100, 50)."""
    fake_sp = FakeSpotify()
    fake_sp.add_playlist("test_playlist")
    tracks = [f"spotify:track:{i}" for i in range(250)]

    add_tracks(fake_sp, tracks, "test_playlist")

    assert fake_sp.call_count("playlist_add_items") == 3
    assert len(fake_sp.playlist_uris("test_playlist")) == 250


def test_add_command_with_url(mock_get_spotify):
    mock_get_spotify.add_playlist("abcdef123")
    result = runner.invoke(
        app,
        ["playlist", "add", "--url", "https://open.spotify.com/playlist/abcdef123"],
        input="spotify:track:12345",
    )
    assert result.exit_code == 0
    assert "spotify:track:12345" in mock_get_spotify.playlist_uris("abcdef123")


def test_add_command_with_id(mock_get_spotify):
    mock_get_spotify.add_playlist("abcdef123")
    result = runner.invoke(app, ["playlist", "add", "--id", "abcdef123"], input="spotify:track:12345")
    assert result.exit_code == 0
    assert "spotify:track:12345" in mock_get_spotify.playlist_uris("abcdef123")


def test_add_command_from_file(mock_get_spotify, tmp_path):
    mock_get_spotify.add_playlist("abcdef123")
    tracks_file = tmp_path / "tracks.txt"
    tracks_file.write_text("spotify:track:1\nspotify:track:2")

    result = runner.invoke(app, ["playlist", "add", "--id", "abcdef123", "--file", str(tracks_file)])

    assert result.exit_code == 0
    uris = mock_get_spotify.playlist_uris("abcdef123")
    assert "spotify:track:1" in uris
    assert "spotify:track:2" in uris


def test_add_command_no_input(mock_get_spotify):
    with patch("src.main.is_interactive", return_value=True):
        result = runner.invoke(app, ["playlist", "add", "--id", "dummy"])
        assert result.exit_code == 1
        assert "No input provided" in result.output


def test_add_command_invalid_url():
    result = runner.invoke(app, ["playlist", "add", "--url", "invalid_url"], input="track")
    assert result.exit_code == 1
    assert "Invalid playlist URL" in result.output
