from typer.testing import CliRunner
from src.main import app, is_interactive
import pytest
import sys

runner = CliRunner()

@pytest.fixture
def mock_consoles(mocker):
    mock_console = mocker.patch("src.main.console")
    mock_err_console = mocker.patch("src.main.err_console")
    # Also patch playlist commands consoles
    mocker.patch("src.commands.playlist.console", mock_console)
    mocker.patch("src.commands.playlist.err_console", mock_err_console)
    return mock_console, mock_err_console

def test_status_command(mocker, mock_consoles):
    mock_console, _ = mock_consoles
    mock_spotify = mocker.patch("src.main.get_spotify")
    mock_sp_instance = mock_spotify.return_value
    mock_sp_instance.current_user.return_value = {"display_name": "Test User", "id": "test_user_id"}

    result = runner.invoke(app, ["status"])
    assert result.exit_code == 0
    # verify console.print was called with expected string
    args, _ = mock_console.print.call_args
    assert "Connected!" in args[0]
    assert "Test User" in args[0]

def test_status_command_failure(mocker, mock_consoles):
    _, mock_err_console = mock_consoles
    mock_spotify = mocker.patch("src.main.get_spotify")
    mock_spotify.side_effect = Exception("Connection Error")

    result = runner.invoke(app, ["status"])
    assert result.exit_code == 0 # It catches exception and prints error, but doesn't exit(1) in status()

    args, _ = mock_err_console.print.call_args
    assert "Status Failed:" in args[0]
    assert "Connection Error" in args[0]

def test_move_command_file(mocker, tmp_path):
    mock_move = mocker.patch("src.main.do_move_tracks")
    mock_spotify = mocker.patch("src.main.get_spotify")

    track_file = tmp_path / "tracks.txt"
    track_file.write_text("spotify:track:123\nspotify:track:456")

    result = runner.invoke(app, ["playlist", "move", "--file", str(track_file), "--from", "src_id", "--to", "dst_id"])

    assert result.exit_code == 0
    mock_move.assert_called_once()
    args, _ = mock_move.call_args
    assert args[1] == ["spotify:track:123", "spotify:track:456"]
    assert args[2] == "src_id"
    assert args[3] == "dst_id"

def test_move_command_empty_file(mocker, tmp_path, mock_consoles):
    mock_console, _ = mock_consoles
    track_file = tmp_path / "tracks.txt"
    track_file.write_text("\n   \n") # Empty file

    result = runner.invoke(app, ["playlist", "move", "--file", str(track_file), "--from", "src_id", "--to", "dst_id"])

    assert result.exit_code == 0
    args, _ = mock_console.print.call_args
    assert "No tracks found" in args[0]

def test_move_command_stdin(mocker):
    mock_move = mocker.patch("src.main.do_move_tracks")
    mock_spotify = mocker.patch("src.main.get_spotify")
    mocker.patch("src.main.is_interactive", return_value=False)

    input_tracks = "spotify:track:123\nspotify:track:456"

    result = runner.invoke(app, ["playlist", "move", "--from", "src_id", "--to", "dst_id"], input=input_tracks)

    assert result.exit_code == 0
    mock_move.assert_called_once()
    args, _ = mock_move.call_args
    assert args[1] == ["spotify:track:123", "spotify:track:456"]

def test_move_command_no_input(mocker, mock_consoles):
    _, mock_err_console = mock_consoles
    mocker.patch("src.main.is_interactive", return_value=True)

    result = runner.invoke(app, ["playlist", "move", "--from", "src_id", "--to", "dst_id"])
    assert result.exit_code == 1

    args, _ = mock_err_console.print.call_args
    assert "Error" in args[0]
    assert "No input provided" in args[0]

def test_move_command_file_not_found(mocker, mock_consoles):
    _, mock_err_console = mock_consoles
    result = runner.invoke(app, ["playlist", "move", "--file", "nonexistent.txt", "--from", "src_id", "--to", "dst_id"])
    assert result.exit_code == 1

    args, _ = mock_err_console.print.call_args
    assert "Error" in args[0]
    assert "does not exist" in args[0]

def test_move_command_exception(mocker, tmp_path, mock_consoles):
    _, mock_err_console = mock_consoles
    mock_move = mocker.patch("src.main.do_move_tracks")
    mock_spotify = mocker.patch("src.main.get_spotify")
    mock_move.side_effect = Exception("Move Error")

    track_file = tmp_path / "tracks.txt"
    track_file.write_text("spotify:track:123")

    result = runner.invoke(app, ["playlist", "move", "--file", str(track_file), "--from", "src_id", "--to", "dst_id"])
    assert result.exit_code == 0

    args, _ = mock_err_console.print.call_args
    assert "Move Failed:" in args[0]
    assert "Move Error" in args[0]

def test_search_command_stdin(mocker):
    mock_spotify = mocker.patch("src.main.get_spotify")
    mocker.patch("src.main.is_interactive", return_value=False)
    mock_sp_instance = mock_spotify.return_value
    mock_sp_instance.search.return_value = {
        'tracks': {
            'items': [{'uri': 'spotify:track:123'}]
        }
    }

    input_text = "Artist - Title\n\n   \n" # Includes empty lines
    result = runner.invoke(app, ["playlist", "search"], input=input_text)

    assert result.exit_code == 0
    assert "spotify:track:123" in result.stdout
    mock_sp_instance.search.assert_called_once_with(q='artist:Artist track:Title', type='track', limit=1)

def test_search_command_not_found(mocker, mock_consoles):
    _, mock_err_console = mock_consoles
    mock_spotify = mocker.patch("src.main.get_spotify")
    mocker.patch("src.main.is_interactive", return_value=False)
    mock_sp_instance = mock_spotify.return_value
    mock_sp_instance.search.return_value = {'tracks': {'items': []}}

    input_text = "Artist - Unknown\n"
    result = runner.invoke(app, ["playlist", "search"], input=input_text)

    assert result.exit_code == 0
    args, _ = mock_err_console.print.call_args
    assert "Not found" in args[0]

def test_search_command_invalid_format(mocker, mock_consoles):
    _, mock_err_console = mock_consoles
    mock_spotify = mocker.patch("src.main.get_spotify")
    mocker.patch("src.main.is_interactive", return_value=False)

    input_text = "Invalid Format\n"
    result = runner.invoke(app, ["playlist", "search"], input=input_text)

    assert result.exit_code == 0
    args, _ = mock_err_console.print.call_args
    assert "Skipping invalid format" in args[0]

def test_search_command_no_input(mocker, mock_consoles):
    _, mock_err_console = mock_consoles
    mocker.patch("src.main.is_interactive", return_value=True)

    result = runner.invoke(app, ["playlist", "search"])
    assert result.exit_code == 1

    args, _ = mock_err_console.print.call_args
    assert "Error" in args[0]

def test_search_command_connection_failed(mocker, mock_consoles):
    _, mock_err_console = mock_consoles
    mock_spotify = mocker.patch("src.main.get_spotify")
    mock_spotify.side_effect = Exception("Connection Error")
    mocker.patch("src.main.is_interactive", return_value=False)

    result = runner.invoke(app, ["playlist", "search"], input="A - B")

    assert result.exit_code == 1
    args, _ = mock_err_console.print.call_args
    assert "Connection Failed:" in args[0]

def test_is_interactive(mocker):
    mocker.patch("sys.stdin.isatty", return_value=True)
    assert is_interactive() is True

    mocker.patch("sys.stdin.isatty", return_value=False)
    assert is_interactive() is False
