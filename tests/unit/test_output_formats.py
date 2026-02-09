from typer.testing import CliRunner
from src.main import app
import pytest
import json
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
            'items': [{'uri': 'spotify:track:12345', 'id': '12345'}]
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

def test_search_output_text(mock_spotify):
    """Test search command with --output text"""
    mock_spotify.search.return_value = {
        'tracks': {
            'items': [{
                'uri': 'spotify:track:12345',
                'id': '12345',
                'name': 'Get Lucky',
                'artists': [{'name': 'Daft Punk'}]
            }]
        }
    }
    with patch('src.main.is_interactive', return_value=False):
        result = runner.invoke(app, ["playlist", "search", "--output", "text"], input="Daft Punk - Get Lucky\n")

        assert result.exit_code == 0
        # Should output "Artist - Title"
        assert "Daft Punk - Get Lucky" in result.stdout

def test_search_output_json(mock_spotify):
    """Test search command with --format json"""
    mock_spotify.search.return_value = {
        'tracks': {
            'items': [{
                'uri': 'spotify:track:12345',
                'id': '12345',
                'name': 'Get Lucky',
                'artists': [{'name': 'Daft Punk'}],
                'album': {'release_date': '2013-05-17'}
            }]
        }
    }
    with patch('src.main.is_interactive', return_value=False):
        # Test both --format and --output as aliases if I decide to implement that way,
        # but the request specifically said --format json
        result = runner.invoke(app, ["playlist", "search", "--format", "json"], input="Daft Punk - Get Lucky\n")

        assert result.exit_code == 0
        output_json = json.loads(result.stdout.strip())
        assert output_json['uri'] == 'spotify:track:12345'
        assert output_json['id'] == '12345'
        assert output_json['name'] == 'Get Lucky'
        assert output_json['artists'] == 'Daft Punk'
        assert output_json['release_date'] == '2013-05-17'

def test_search_output_json_via_output_flag(mock_spotify):
    """Test search command with --output json"""
    mock_spotify.search.return_value = {
        'tracks': {
            'items': [{
                'uri': 'spotify:track:12345',
                'id': '12345',
                'name': 'Get Lucky',
                'artists': [{'name': 'Daft Punk'}],
                'album': {'release_date': '2013-05-17'}
            }]
        }
    }
    with patch('src.main.is_interactive', return_value=False):
        result = runner.invoke(app, ["playlist", "search", "--output", "json"], input="Daft Punk - Get Lucky\n")

        assert result.exit_code == 0
        output_json = json.loads(result.stdout.strip())
        assert output_json['uri'] == 'spotify:track:12345'
