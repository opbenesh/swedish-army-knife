import json
from unittest.mock import patch

from typer.testing import CliRunner

from src.main import app

runner = CliRunner()

_TRACK = {
    "uri": "spotify:track:12345",
    "id": "12345",
    "name": "Get Lucky",
    "artists": [{"name": "Daft Punk"}],
    "album": {"release_date": "2013-05-17"},
}


def test_search_output_id(mock_get_spotify):
    mock_get_spotify.set_default_search_result(_TRACK)
    with patch("src.main.is_interactive", return_value=False):
        result = runner.invoke(app, ["playlist", "search", "--output", "id"], input="Artist - Title\n")

    assert result.exit_code == 0
    assert "12345" in result.stdout
    assert "spotify:track:" not in result.stdout


def test_list_output_id(mock_get_spotify):
    mock_get_spotify.add_playlist("pl_id", tracks=[_TRACK])
    result = runner.invoke(app, ["playlist", "list", "--id", "pl_id", "--output", "id"])
    assert result.exit_code == 0
    assert "12345" in result.stdout
    assert "Artist" not in result.stdout


def test_list_output_uri(mock_get_spotify):
    mock_get_spotify.add_playlist("pl_id", tracks=[_TRACK])
    result = runner.invoke(app, ["playlist", "list", "--id", "pl_id", "--output", "uri"])
    assert result.exit_code == 0
    assert "spotify:track:12345" in result.stdout


def test_search_output_text(mock_get_spotify):
    mock_get_spotify.set_default_search_result(_TRACK)
    with patch("src.main.is_interactive", return_value=False):
        result = runner.invoke(app, ["playlist", "search", "--output", "text"], input="Daft Punk - Get Lucky\n")

    assert result.exit_code == 0
    assert "Daft Punk - Get Lucky" in result.stdout


def test_search_output_json(mock_get_spotify):
    mock_get_spotify.set_default_search_result(_TRACK)
    with patch("src.main.is_interactive", return_value=False):
        result = runner.invoke(app, ["playlist", "search", "--format", "json"], input="Daft Punk - Get Lucky\n")

    assert result.exit_code == 0
    data = json.loads(result.stdout.strip())
    assert data["uri"] == "spotify:track:12345"
    assert data["id"] == "12345"
    assert data["name"] == "Get Lucky"
    assert data["artists"] == "Daft Punk"
    assert data["release_date"] == "2013-05-17"


def test_search_output_json_via_output_flag(mock_get_spotify):
    mock_get_spotify.set_default_search_result(_TRACK)
    with patch("src.main.is_interactive", return_value=False):
        result = runner.invoke(app, ["playlist", "search", "--output", "json"], input="Daft Punk - Get Lucky\n")

    assert result.exit_code == 0
    data = json.loads(result.stdout.strip())
    assert data["uri"] == "spotify:track:12345"
