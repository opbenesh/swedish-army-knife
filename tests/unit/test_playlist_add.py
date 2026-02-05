import pytest
from unittest.mock import MagicMock, patch
from typer.testing import CliRunner
from src.main import app
from src.commands.playlist import add_tracks

runner = CliRunner()

@pytest.fixture
def mock_spotify():
    """Create a mock Spotify client."""
    with patch('src.main.get_spotify') as mock_get:
        sp = MagicMock()
        mock_get.return_value = sp
        yield sp

def test_add_tracks_logic(mock_spotify):
    """Test the core add_tracks function logic including batching."""
    sp = mock_spotify
    playlist_id = "test_playlist"
    # Create 250 tracks to test batching (batches of 100)
    tracks = [f"spotify:track:{i}" for i in range(250)]
    
    add_tracks(sp, tracks, playlist_id)
    
    # Should be called 3 times: 100, 100, 50
    assert sp.playlist_add_items.call_count == 3
    sp.playlist_add_items.assert_any_call(playlist_id, tracks[0:100])
    sp.playlist_add_items.assert_any_call(playlist_id, tracks[100:200])
    sp.playlist_add_items.assert_any_call(playlist_id, tracks[200:250])

def test_add_command_with_url(mock_spotify):
    """Test CLI add command using playlist URL."""
    playlist_url = "https://open.spotify.com/playlist/abcdef123"
    playlist_id = "abcdef123"
    track_uri = "spotify:track:12345"
    
    result = runner.invoke(app, ['playlist', 'add', '--url', playlist_url], input=track_uri)
    
    assert result.exit_code == 0
    mock_spotify.playlist_add_items.assert_called_once_with(playlist_id, [track_uri])

def test_add_command_with_id(mock_spotify):
    """Test CLI add command using playlist ID."""
    playlist_id = "abcdef123"
    track_uri = "spotify:track:12345"
    
    result = runner.invoke(app, ['playlist', 'add', '--id', playlist_id], input=track_uri)
    
    assert result.exit_code == 0
    mock_spotify.playlist_add_items.assert_called_once_with(playlist_id, [track_uri])

def test_add_command_from_file(mock_spotify, tmp_path):
    """Test CLI add command reading from a file."""
    playlist_id = "abcdef123"
    tracks_file = tmp_path / "tracks.txt"
    tracks_file.write_text("spotify:track:1\nspotify:track:2")
    
    result = runner.invoke(app, ['playlist', 'add', '--id', playlist_id, '--file', str(tracks_file)])
    
    assert result.exit_code == 0
    mock_spotify.playlist_add_items.assert_called_once_with(playlist_id, ["spotify:track:1", "spotify:track:2"])

def test_add_command_no_input(mock_spotify):
    """Test error when no input (file or stdin) provided."""
    result = runner.invoke(app, ['playlist', 'add', '--id', 'dummy'])
    # Typer/Click handles isatty check differently in tests, but it fails if no input provided
    # Here we expect it to fail or print "No tracks found" depending on how isatty behaves in test
    
    # Actually, in the code we simulate empty stdin if no file.
    # If is_interactive() is mocked or behaves as TTY, it raises Exit(1).
    # If not TTY but empty, it prints "No tracks found".
    # Let's mock is_interactive to True
    with patch('src.main.is_interactive', return_value=True):
        result = runner.invoke(app, ['playlist', 'add', '--id', 'dummy'])
        assert result.exit_code == 1
        assert "No input provided" in result.output

def test_add_command_invalid_url():
    """Test invalid playlist URL."""
    result = runner.invoke(app, ['playlist', 'add', '--url', 'invalid_url'], input="track")
    assert result.exit_code == 1
    assert "Invalid playlist URL" in result.output
