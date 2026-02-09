from typer.testing import CliRunner
from src.main import app
import pytest

runner = CliRunner()

@pytest.fixture
def mock_consoles(mocker):
    # Mock both main and command consoles to be safe
    mock_console = mocker.patch("src.main.console")
    mock_err_console = mocker.patch("src.main.err_console")
    return mock_console, mock_err_console

def test_find_playlist_success(mocker, mock_consoles):
    mock_console, _ = mock_consoles
    mock_spotify = mocker.patch("src.main.get_spotify")
    mock_sp_instance = mock_spotify.return_value

    # Mocking playlists
    mock_sp_instance.current_user_playlists.return_value = {
        'items': [
            {'name': 'Other Playlist', 'id': 'id1'},
            {'name': 'My Playlist', 'id': 'target_id'}
        ],
        'next': None
    }

    # We need to mock do_find_playlist if we are testing the CLI command in main.py
    # but since we haven't implemented it yet, this test will fail as expected.
    # Actually, if I haven't added the command to app, it will fail with "No such command 'find'"

    result = runner.invoke(app, ["playlist", "find", "My Playlist"])

    assert result.exit_code == 0
    mock_console.print.assert_called_with("target_id")

def test_find_playlist_not_found(mocker, mock_consoles):
    _, mock_err_console = mock_consoles
    mock_spotify = mocker.patch("src.main.get_spotify")
    mock_sp_instance = mock_spotify.return_value

    mock_sp_instance.current_user_playlists.return_value = {
        'items': [
            {'name': 'Other Playlist', 'id': 'id1'}
        ],
        'next': None
    }

    result = runner.invoke(app, ["playlist", "find", "Nonexistent"])

    assert result.exit_code == 1
    # Check that the Error message was printed (it might be the first or second call depending on how it's mocked)
    # Since we added `except typer.Exit: raise`, it should be the Error: call.
    found_error = False
    for call in mock_err_console.print.call_args_list:
        if "Playlist 'Nonexistent' not found" in call[0][0]:
            found_error = True
            break
    assert found_error

def test_find_playlist_pagination(mocker, mock_consoles):
    mock_console, _ = mock_consoles
    mock_spotify = mocker.patch("src.main.get_spotify")
    mock_sp_instance = mock_spotify.return_value

    # Page 1
    page1 = {
        'items': [{'name': 'Other 1', 'id': 'id1'}],
        'next': 'url_to_page2'
    }
    # Page 2
    page2 = {
        'items': [{'name': 'My Playlist', 'id': 'target_id'}],
        'next': None
    }

    mock_sp_instance.current_user_playlists.return_value = page1
    mock_sp_instance.next.return_value = page2

    result = runner.invoke(app, ["playlist", "find", "My Playlist"])

    assert result.exit_code == 0
    mock_console.print.assert_called_with("target_id")
    mock_sp_instance.next.assert_called_once_with(page1)
