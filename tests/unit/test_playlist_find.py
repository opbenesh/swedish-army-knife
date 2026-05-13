from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from src.main import app

runner = CliRunner()


def test_find_playlist_success(mock_get_spotify, mock_consoles):
    mock_console, _ = mock_consoles
    mock_get_spotify.add_playlist("target_id", name="My Playlist")
    mock_get_spotify.add_playlist("id1", name="Other Playlist")

    result = runner.invoke(app, ["playlist", "find", "My Playlist"])

    assert result.exit_code == 0
    mock_console.print.assert_called_with("target_id")


def test_find_playlist_not_found(mock_get_spotify, mock_consoles):
    _, mock_err_console = mock_consoles
    mock_get_spotify.add_playlist("id1", name="Other Playlist")

    result = runner.invoke(app, ["playlist", "find", "Nonexistent"])

    assert result.exit_code == 1
    found_error = any(
        "Playlist 'Nonexistent' not found" in call[0][0]
        for call in mock_err_console.print.call_args_list
    )
    assert found_error


def test_find_playlist_pagination():
    """Pagination: playlist found on second page (uses MagicMock to simulate multi-page)."""
    with patch("src.main.get_spotify") as mock_get:
        sp = MagicMock()
        mock_get.return_value = sp

        page1 = {"items": [{"name": "Other 1", "id": "id1"}], "next": "url_to_page2"}
        page2 = {"items": [{"name": "My Playlist", "id": "target_id"}], "next": None}
        sp.current_user_playlists.return_value = page1
        sp.next.return_value = page2

        result = runner.invoke(app, ["playlist", "find", "My Playlist"])

        assert result.exit_code == 0
        sp.next.assert_called_once_with(page1)
