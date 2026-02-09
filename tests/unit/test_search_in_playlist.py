from typer.testing import CliRunner
from src.main import app
import pytest

runner = CliRunner()

def test_search_command_in_playlist(mocker):
    mock_spotify = mocker.patch("src.main.get_spotify")
    mocker.patch("src.main.is_interactive", return_value=False)
    mock_sp_instance = mock_spotify.return_value

    # Mock playlist tracks
    mock_sp_instance.playlist_tracks.return_value = {
        'items': [
            {
                'track': {
                    'id': 'track1_id',
                    'uri': 'spotify:track:track1_uri',
                    'name': 'Get Lucky',
                    'artists': [{'name': 'Daft Punk'}]
                }
            },
            {
                'track': {
                    'id': 'track2_id',
                    'uri': 'spotify:track:track2_uri',
                    'name': 'Lose Yourself to Dance',
                    'artists': [{'name': 'Daft Punk'}]
                }
            }
        ],
        'next': None
    }

    input_text = "Daft Punk - Get Luck\n" # Slightly misspelled
    result = runner.invoke(app, ["playlist", "search", "--in-playlist", "some_playlist_id"], input=input_text)

    assert result.exit_code == 0
    assert "spotify:track:track1_uri" in result.stdout
    # Ensure it didn't call the global search
    assert mock_sp_instance.search.call_count == 0
    # Ensure it fetched playlist tracks
    mock_sp_instance.playlist_tracks.assert_any_call("some_playlist_id")
