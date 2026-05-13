from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from src.main import app

runner = CliRunner()


def test_list_tracks_with_url(mock_get_spotify):
    mock_get_spotify.add_playlist("abc123", tracks=[
        {"id": "t1", "uri": "spotify:track:t1", "name": "Song One", "artists": [{"name": "Artist A"}], "album": {}},
        {"id": "t2", "uri": "spotify:track:t2", "name": "Song Two", "artists": [{"name": "Artist B"}, {"name": "Artist C"}], "album": {}},
    ])

    result = runner.invoke(app, ["playlist", "list", "--url", "https://open.spotify.com/playlist/abc123"])

    assert result.exit_code == 0
    assert "Artist A - Song One" in result.output
    assert "Artist B, Artist C - Song Two" in result.output


def test_list_tracks_with_id(mock_get_spotify):
    mock_get_spotify.add_playlist("my_playlist_id", tracks=[
        {"id": "t1", "uri": "spotify:track:t1", "name": "Test Track", "artists": [{"name": "Test Artist"}], "album": {}},
    ])

    result = runner.invoke(app, ["playlist", "list", "--id", "my_playlist_id"])

    assert result.exit_code == 0
    assert "Test Artist - Test Track" in result.output


def test_list_tracks_pagination():
    """Pagination fetches all tracks from large playlists (uses MagicMock to simulate multi-page)."""
    with patch("src.main.get_spotify") as mock_get:
        sp = MagicMock()
        mock_get.return_value = sp

        page1 = {
            "items": [{"track": {"id": str(i), "uri": f"spotify:track:{i}", "name": f"Track {i}", "artists": [{"name": f"Artist {i}"}]}} for i in range(100)],
            "next": "https://api.spotify.com/next",
        }
        page2 = {
            "items": [{"track": {"id": str(i), "uri": f"spotify:track:{i}", "name": f"Track {i}", "artists": [{"name": f"Artist {i}"}]}} for i in range(100, 150)],
            "next": None,
        }
        sp.playlist_tracks.return_value = page1
        sp.next.return_value = page2

        result = runner.invoke(app, ["playlist", "list", "--id", "large_playlist"])

        assert result.exit_code == 0
        assert "Artist 0 - Track 0" in result.output
        assert "Artist 99 - Track 99" in result.output
        assert "Artist 100 - Track 100" in result.output
        assert "Artist 149 - Track 149" in result.output
        sp.next.assert_called_once_with(page1)


def test_list_tracks_handles_null_tracks(mock_get_spotify):
    mock_get_spotify.add_playlist("pl", tracks=[
        {"id": "t1", "uri": "spotify:track:t1", "name": "Valid Track", "artists": [{"name": "Valid Artist"}], "album": {}},
        {"id": "t2", "uri": "spotify:track:t2", "name": "Another Track", "artists": [{"name": "Another Artist"}], "album": {}},
    ])
    # Manually inject a None track
    mock_get_spotify._playlists["pl"]["tracks"].insert(1, None)

    result = runner.invoke(app, ["playlist", "list", "--id", "pl"])

    assert result.exit_code == 0
    assert "Valid Artist - Valid Track" in result.output
    assert "Another Artist - Another Track" in result.output


def test_list_tracks_invalid_url(mock_get_spotify):
    result = runner.invoke(app, ["playlist", "list", "--url", "https://invalid-url.com/not-a-playlist"])
    assert result.exit_code == 1
    assert "Invalid playlist URL" in result.output


def test_list_tracks_no_input():
    with patch("src.main.get_spotify"):
        result = runner.invoke(app, ["playlist", "list"])
    assert result.exit_code == 1
    assert "Provide --url or --id" in result.output
