
from typer.testing import CliRunner

from src.main import app, is_interactive

# module-level runner kept for tests that don't need FakeSpotify
runner = CliRunner()


def test_status_command(mock_get_spotify, mock_consoles):
    mock_console, _ = mock_consoles
    result = runner.invoke(app, ["status"])
    assert result.exit_code == 0
    args, _ = mock_console.print.call_args
    assert "Connected!" in args[0]
    assert "Test User" in args[0]


def test_status_command_failure(mocker, mock_consoles):
    _, mock_err_console = mock_consoles
    mocker.patch("src.main.get_spotify", side_effect=Exception("Connection Error"))

    result = runner.invoke(app, ["status"])
    assert result.exit_code == 1

    args, _ = mock_err_console.print.call_args
    assert "Status Failed:" in args[0]
    assert "Connection Error" in args[0]


def test_move_command_file(mock_get_spotify, mocker, tmp_path):
    mock_move = mocker.patch("src.main.do_move_tracks")

    track_file = tmp_path / "tracks.txt"
    track_file.write_text("spotify:track:123\nspotify:track:456")

    result = runner.invoke(app, ["playlist", "move", "--file", str(track_file), "--from", "src_id", "--to", "dst_id"])

    assert result.exit_code == 0
    mock_move.assert_called_once()
    args, _ = mock_move.call_args
    assert args[1] == ["spotify:track:123", "spotify:track:456"]
    assert args[2] == "src_id"
    assert args[3] == "dst_id"


def test_move_command_empty_file(mock_get_spotify, mock_consoles, tmp_path):
    mock_console, _ = mock_consoles
    track_file = tmp_path / "tracks.txt"
    track_file.write_text("\n   \n")

    result = runner.invoke(app, ["playlist", "move", "--file", str(track_file), "--from", "src_id", "--to", "dst_id"])

    assert result.exit_code == 0
    args, _ = mock_console.print.call_args
    assert "No tracks found" in args[0]


def test_move_command_stdin(mock_get_spotify, mocker):
    mock_move = mocker.patch("src.main.do_move_tracks")
    mocker.patch("src.main.is_interactive", return_value=False)

    result = runner.invoke(
        app,
        ["playlist", "move", "--from", "src_id", "--to", "dst_id"],
        input="spotify:track:123\nspotify:track:456",
    )

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


def test_move_command_file_not_found(mock_consoles):
    _, mock_err_console = mock_consoles
    result = runner.invoke(app, ["playlist", "move", "--file", "nonexistent.txt", "--from", "src_id", "--to", "dst_id"])
    assert result.exit_code == 1

    args, _ = mock_err_console.print.call_args
    assert "Error" in args[0]
    assert "does not exist" in args[0]


def test_move_command_exception(mock_get_spotify, mocker, mock_consoles, tmp_path):
    _, mock_err_console = mock_consoles
    mocker.patch("src.main.do_move_tracks", side_effect=Exception("Move Error"))

    track_file = tmp_path / "tracks.txt"
    track_file.write_text("spotify:track:123")

    result = runner.invoke(app, ["playlist", "move", "--file", str(track_file), "--from", "src_id", "--to", "dst_id"])
    assert result.exit_code == 1

    args, _ = mock_err_console.print.call_args
    assert "Move Failed:" in args[0]
    assert "Move Error" in args[0]


def test_search_command_stdin(mocker, mock_get_spotify):
    mocker.patch("src.main.is_interactive", return_value=False)
    mock_get_spotify.set_search_result(
        "artist:Artist track:Title",
        {"uri": "spotify:track:123", "id": "123", "name": "Title", "artists": [{"name": "Artist"}], "album": {"release_date": "2020"}},
    )

    result = runner.invoke(app, ["playlist", "search"], input="Artist - Title\n\n   \n")

    assert result.exit_code == 0
    assert "spotify:track:123" in result.stdout
    assert mock_get_spotify.call_count("search") == 1


def test_search_command_not_found(mocker, mock_get_spotify, mock_consoles):
    _, mock_err_console = mock_consoles
    mocker.patch("src.main.is_interactive", return_value=False)

    result = runner.invoke(app, ["playlist", "search"], input="Artist - Unknown\n")

    assert result.exit_code == 0
    args, _ = mock_err_console.print.call_args
    assert "Not found" in args[0]


def test_search_command_invalid_format(mocker, mock_get_spotify, mock_consoles):
    _, mock_err_console = mock_consoles
    mocker.patch("src.main.is_interactive", return_value=False)

    result = runner.invoke(app, ["playlist", "search"], input="Invalid Format\n")

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
    mocker.patch("src.main.get_spotify", side_effect=Exception("Connection Error"))
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


def test_create_playlist_command(mock_get_spotify, mock_consoles):
    mock_console, _ = mock_consoles
    result = runner.invoke(app, ["playlist", "create", "--name", "New Playlist"])

    assert result.exit_code == 0
    # FakeSpotify creates a URI like spotify:playlist:pl_new_playlist
    args, _ = mock_console.print.call_args
    assert "spotify:playlist:" in args[0]


def test_move_command_strict(mock_get_spotify, mocker):
    mock_move = mocker.patch("src.main.do_move_tracks")
    mocker.patch("src.main.is_interactive", return_value=False)

    result = runner.invoke(
        app,
        ["playlist", "move", "--from", "src_id", "--to", "dst_id", "--strict"],
        input="spotify:track:123",
    )

    assert result.exit_code == 0
    mock_move.assert_called_once_with(
        mock_get_spotify, ["spotify:track:123"], "src_id", "dst_id", strict=True
    )


def test_move_create_creates_playlist_when_missing(mock_get_spotify, mocker):
    mock_move = mocker.patch("src.main.do_move_tracks")
    mocker.patch("src.main.is_interactive", return_value=False)

    result = runner.invoke(
        app,
        ["playlist", "move", "--from", "src_id", "--to", "My New Playlist", "--create"],
        input="spotify:track:123",
    )

    assert result.exit_code == 0
    # Playlist was created; FakeSpotify derives the ID from the name
    args, _ = mock_move.call_args
    assert args[3] == "pl_my_new_playlist"


def test_move_create_reuses_existing_playlist(mock_get_spotify, mocker):
    mock_move = mocker.patch("src.main.do_move_tracks")
    mocker.patch("src.main.is_interactive", return_value=False)
    mock_get_spotify.add_playlist("existing_id", name="Existing Playlist")

    result = runner.invoke(
        app,
        ["playlist", "move", "--from", "src_id", "--to", "Existing Playlist", "--create"],
        input="spotify:track:123",
    )

    assert result.exit_code == 0
    args, _ = mock_move.call_args
    assert args[3] == "existing_id"


def test_move_liked_auto_fetches_when_no_input(mock_get_spotify, mocker):
    mock_move = mocker.patch("src.main.do_move_tracks")
    mocker.patch("src.main.is_interactive", return_value=True)
    mock_get_spotify.add_saved_tracks(["spotify:track:1", "spotify:track:2"])
    mock_get_spotify.add_playlist("dest_id")

    result = runner.invoke(app, ["playlist", "move", "--from", "liked", "--to", "dest_id"])

    assert result.exit_code == 0
    args, _ = mock_move.call_args
    assert set(args[1]) == {"spotify:track:1", "spotify:track:2"}


def test_move_liked_still_accepts_explicit_stdin(mock_get_spotify, mocker):
    mock_move = mocker.patch("src.main.do_move_tracks")
    mocker.patch("src.main.is_interactive", return_value=False)
    mock_get_spotify.add_saved_tracks(["spotify:track:ignored"])

    result = runner.invoke(
        app,
        ["playlist", "move", "--from", "liked", "--to", "dest_id"],
        input="spotify:track:explicit\n",
    )

    assert result.exit_code == 0
    args, _ = mock_move.call_args
    assert args[1] == ["spotify:track:explicit"]


def test_move_liked_auto_empty(mock_get_spotify, mock_consoles, mocker):
    mock_console, _ = mock_consoles
    mocker.patch("src.main.is_interactive", return_value=True)

    result = runner.invoke(app, ["playlist", "move", "--from", "liked", "--to", "dest_id"])

    assert result.exit_code == 0
    args, _ = mock_console.print.call_args
    assert "No liked tracks found" in args[0]


def test_list_by_name(mock_get_spotify):
    mock_get_spotify.add_playlist("real_id", name="My Playlist", tracks=["spotify:track:abc"])

    result = runner.invoke(app, ["playlist", "list", "--id", "My Playlist", "--output", "uri"])

    assert result.exit_code == 0
    assert "spotify:track:abc" in result.stdout


def test_add_create_flag(mock_get_spotify, mocker):
    mock_add = mocker.patch("src.main.do_add_tracks")
    mocker.patch("src.main.is_interactive", return_value=False)

    result = runner.invoke(
        app,
        ["playlist", "add", "--id", "New Playlist", "--create"],
        input="spotify:track:123\n",
    )

    assert result.exit_code == 0
    args, _ = mock_add.call_args
    # FakeSpotify created "pl_new_playlist"
    assert args[2] == "pl_new_playlist"


def test_search_in_playlist_by_name(mock_get_spotify, mocker):
    mock_get_spotify.add_playlist("real_id", name="My Playlist")
    mock_search = mocker.patch("src.main.do_search_tracks", return_value=[])
    mocker.patch("src.main.is_interactive", return_value=False)

    runner.invoke(
        app,
        ["playlist", "search", "--in-playlist", "My Playlist"],
        input="Artist - Title\n",
    )

    _, kwargs = mock_search.call_args
    assert kwargs["playlist_id"] == "real_id"
