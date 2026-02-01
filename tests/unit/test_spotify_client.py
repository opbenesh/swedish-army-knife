from unittest.mock import MagicMock
import pytest
from src.spotify_client import SpotifyClient, get_spotify

def test_spotify_client_initialization(mocker, monkeypatch):
    monkeypatch.setenv("SPOTIPY_CLIENT_ID", "test_id")
    monkeypatch.setenv("SPOTIPY_CLIENT_SECRET", "test_secret")

    mock_oauth = mocker.patch("src.spotify_client.SpotifyOAuth")

    client = SpotifyClient()
    assert client.sp_oauth is not None

def test_spotify_client_missing_credentials(mocker, monkeypatch, capsys):
    monkeypatch.delenv("SPOTIPY_CLIENT_ID", raising=False)
    monkeypatch.delenv("SPOTIPY_CLIENT_SECRET", raising=False)

    with pytest.raises(SystemExit):
        SpotifyClient()

    captured = capsys.readouterr()
    # Now that we use err_console, output is in stderr
    assert "Error" in captured.err
    assert "Spotify credentials not found" in captured.err

def test_get_client_cached_token(mocker, monkeypatch):
    monkeypatch.setenv("SPOTIPY_CLIENT_ID", "test_id")
    monkeypatch.setenv("SPOTIPY_CLIENT_SECRET", "test_secret")

    mock_oauth = mocker.patch("src.spotify_client.SpotifyOAuth")
    mock_oauth_instance = mock_oauth.return_value
    mock_oauth_instance.get_cached_token.return_value = {"access_token": "fake_token"}

    mock_spotify = mocker.patch("spotipy.Spotify")

    client = SpotifyClient()
    sp = client.get_client()

    assert sp is not None
    mock_spotify.assert_called_once()

def test_get_client_no_cached_token(mocker, monkeypatch, capsys):
    monkeypatch.setenv("SPOTIPY_CLIENT_ID", "test_id")
    monkeypatch.setenv("SPOTIPY_CLIENT_SECRET", "test_secret")

    mock_oauth = mocker.patch("src.spotify_client.SpotifyOAuth")
    mock_oauth_instance = mock_oauth.return_value
    mock_oauth_instance.get_cached_token.return_value = None
    mock_oauth_instance.get_authorize_url.return_value = "http://auth.url"

    mock_spotify = mocker.patch("spotipy.Spotify")

    client = SpotifyClient()
    sp = client.get_client()

    captured = capsys.readouterr()
    # 'Initial authentication required' is printed via console.print (stdout)
    assert "Initial authentication required" in captured.out

    assert sp is not None
    mock_spotify.assert_called_once()

def test_get_spotify_helper(mocker, monkeypatch):
    monkeypatch.setenv("SPOTIPY_CLIENT_ID", "test_id")
    monkeypatch.setenv("SPOTIPY_CLIENT_SECRET", "test_secret")

    mock_client_cls = mocker.patch("src.spotify_client.SpotifyClient")
    mock_client_instance = mock_client_cls.return_value
    mock_client_instance.get_client.return_value = "mock_spotify_object"

    result = get_spotify()
    assert result == "mock_spotify_object"
