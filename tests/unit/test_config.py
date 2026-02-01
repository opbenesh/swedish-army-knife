import os
import pytest
from src.config import Settings

def test_config_loaded_from_env(monkeypatch):
    monkeypatch.setenv("SPOTIPY_CLIENT_ID", "test_id")
    monkeypatch.setenv("SPOTIPY_CLIENT_SECRET", "test_secret")
    monkeypatch.setenv("SPOTIPY_REDIRECT_URI", "http://localhost:8888/callback")

    settings = Settings()
    assert settings.SPOTIPY_CLIENT_ID == "test_id"
    assert settings.SPOTIPY_CLIENT_SECRET == "test_secret"
    assert settings.SPOTIPY_REDIRECT_URI == "http://localhost:8888/callback"
    assert settings.is_spotify_configured is True

def test_config_missing_credentials(monkeypatch):
    monkeypatch.delenv("SPOTIPY_CLIENT_ID", raising=False)
    monkeypatch.delenv("SPOTIPY_CLIENT_SECRET", raising=False)

    settings = Settings()
    assert settings.is_spotify_configured is False
