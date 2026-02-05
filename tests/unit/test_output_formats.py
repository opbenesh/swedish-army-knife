from typer.testing import CliRunner
from src.main import app
import pytest
from unittest.mock import MagicMock, patch

runner = CliRunner()

@pytest.fixture
def mock_spotify():
    with patch('src.main.get_spotify') as mock_get:
        sp = MagicMock()
        mock_get.return_value = sp
        yield sp

def test_search_output_id(mock_spotify):
    """Test search command with --output id"""
    mock_spotify.search.return_value = {
        'tracks': {
            'items': [{'uri': 'spotify:track:12345'}]
        }
    }
    with patch('src.main.is_interactive', return_value=False):
        result = runner.invoke(app, ["playlist", "search", "--output", "id"], input="Artist - Title\n")

        assert result.exit_code == 0
        assert "12345" in result.stdout
        assert "spotify:track:" not in result.stdout

def test_list_output_id(mock_spotify):
    """Test list command with --output id"""
    mock_spotify.playlist_tracks.return_value = {
        'items': [
            {'track': {'name': 'Song', 'artists': [{'name': 'Artist'}], 'id': '12345', 'uri': 'spotify:track:12345'}},
        ],
        'next': None
    }
    mock_spotify.next.return_value = None

    result = runner.invoke(app, ['playlist', 'list', '--id', 'pl_id', '--output', 'id'])

    assert result.exit_code == 0
    assert "12345" in result.stdout
    assert "Artist" not in result.stdout

def test_list_output_uri(mock_spotify):
    """Test list command with --output uri"""
    mock_spotify.playlist_tracks.return_value = {
        'items': [
            {'track': {'name': 'Song', 'artists': [{'name': 'Artist'}], 'id': '12345', 'uri': 'spotify:track:12345'}},
        ],
        'next': None
    }
    mock_spotify.next.return_value = None

    result = runner.invoke(app, ['playlist', 'list', '--id', 'pl_id', '--output', 'uri'])

    assert result.exit_code == 0
    assert "spotify:track:12345" in result.stdout
