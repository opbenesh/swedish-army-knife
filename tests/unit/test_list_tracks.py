import pytest
from unittest.mock import MagicMock, patch
from typer.testing import CliRunner
from src.main import app

runner = CliRunner()


@pytest.fixture
def mock_spotify():
    """Create a mock Spotify client."""
    with patch('src.main.get_spotify') as mock_get:
        sp = MagicMock()
        mock_get.return_value = sp
        yield sp


def test_list_tracks_with_url(mock_spotify, capsys):
    """Test listing tracks using a playlist URL."""
    mock_spotify.playlist_tracks.return_value = {
        'items': [
            {'track': {'name': 'Song One', 'artists': [{'name': 'Artist A'}]}},
            {'track': {'name': 'Song Two', 'artists': [{'name': 'Artist B'}, {'name': 'Artist C'}]}},
        ],
        'next': None
    }
    mock_spotify.next.return_value = None
    
    result = runner.invoke(app, ['playlist', 'list', '--url', 'https://open.spotify.com/playlist/abc123'])
    
    assert result.exit_code == 0
    assert 'Artist A - Song One' in result.output
    assert 'Artist B, Artist C - Song Two' in result.output
    mock_spotify.playlist_tracks.assert_called_once_with('abc123')


def test_list_tracks_with_id(mock_spotify):
    """Test listing tracks using a playlist ID directly."""
    mock_spotify.playlist_tracks.return_value = {
        'items': [
            {'track': {'name': 'Test Track', 'artists': [{'name': 'Test Artist'}]}},
        ],
        'next': None
    }
    
    result = runner.invoke(app, ['playlist', 'list', '--id', 'my_playlist_id'])
    
    assert result.exit_code == 0
    assert 'Test Artist - Test Track' in result.output
    mock_spotify.playlist_tracks.assert_called_once_with('my_playlist_id')


def test_list_tracks_pagination(mock_spotify):
    """Test that pagination fetches all tracks from large playlists."""
    # First page of results
    page1 = {
        'items': [{'track': {'name': f'Track {i}', 'artists': [{'name': f'Artist {i}'}]}} for i in range(100)],
        'next': 'https://api.spotify.com/next_page'
    }
    # Second page of results
    page2 = {
        'items': [{'track': {'name': f'Track {i}', 'artists': [{'name': f'Artist {i}'}]}} for i in range(100, 150)],
        'next': None
    }
    
    mock_spotify.playlist_tracks.return_value = page1
    mock_spotify.next.return_value = page2
    
    result = runner.invoke(app, ['playlist', 'list', '--id', 'large_playlist'])
    
    assert result.exit_code == 0
    # Verify we got tracks from both pages
    assert 'Artist 0 - Track 0' in result.output
    assert 'Artist 99 - Track 99' in result.output
    assert 'Artist 100 - Track 100' in result.output
    assert 'Artist 149 - Track 149' in result.output
    # Verify pagination was used
    mock_spotify.next.assert_called_once_with(page1)


def test_list_tracks_handles_null_tracks(mock_spotify):
    """Test that null tracks (local/unavailable) are skipped gracefully."""
    mock_spotify.playlist_tracks.return_value = {
        'items': [
            {'track': {'name': 'Valid Track', 'artists': [{'name': 'Valid Artist'}]}},
            {'track': None},  # Local or unavailable track
            {'track': {'name': 'Another Track', 'artists': [{'name': 'Another Artist'}]}},
        ],
        'next': None
    }
    
    result = runner.invoke(app, ['playlist', 'list', '--id', 'playlist_with_nulls'])
    
    assert result.exit_code == 0
    assert 'Valid Artist - Valid Track' in result.output
    assert 'Another Artist - Another Track' in result.output


def test_list_tracks_invalid_url(mock_spotify):
    """Test error handling for invalid playlist URL."""
    result = runner.invoke(app, ['playlist', 'list', '--url', 'https://invalid-url.com/not-a-playlist'])
    
    assert result.exit_code == 1
    assert 'Invalid playlist URL' in result.output


def test_list_tracks_no_input():
    """Test error when neither URL nor ID is provided."""
    with patch('src.main.get_spotify'):
        result = runner.invoke(app, ['playlist', 'list'])
    
    assert result.exit_code == 1
    assert 'Provide --url or --id' in result.output
