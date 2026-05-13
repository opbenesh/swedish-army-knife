
from typer.testing import CliRunner

from src.main import app

runner = CliRunner()


def test_search_command_in_playlist(mock_get_spotify, mocker):
    mocker.patch("src.main.is_interactive", return_value=False)
    mock_get_spotify.add_playlist("some_playlist_id", tracks=[
        {"id": "track1_id", "uri": "spotify:track:track1_uri", "name": "Get Lucky", "artists": [{"name": "Daft Punk"}], "album": {}},
        {"id": "track2_id", "uri": "spotify:track:track2_uri", "name": "Lose Yourself to Dance", "artists": [{"name": "Daft Punk"}], "album": {}},
    ])

    result = runner.invoke(
        app,
        ["playlist", "search", "--in-playlist", "some_playlist_id"],
        input="Daft Punk - Get Luck\n",  # slightly misspelled
    )

    assert result.exit_code == 0
    assert "spotify:track:track1_uri" in result.stdout
    # Global search was not called
    assert mock_get_spotify.call_count("search") == 0
