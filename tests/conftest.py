from __future__ import annotations

from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from tests.fake_spotify import FakeSpotify


@pytest.fixture
def fake_sp() -> FakeSpotify:
    return FakeSpotify()


@pytest.fixture
def cli_runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def mock_get_spotify(fake_sp: FakeSpotify):
    """Patch src.main.get_spotify to return a FakeSpotify. Yields the FakeSpotify instance."""
    with patch("src.main.get_spotify", return_value=fake_sp):
        yield fake_sp


@pytest.fixture
def mock_consoles(mocker):
    """Silence Rich console output and return (console, err_console) mocks."""
    mock_console = mocker.patch("src.main.console")
    mock_err_console = mocker.patch("src.main.err_console")
    mocker.patch("src.commands.playlist.console", mock_console)
    mocker.patch("src.commands.playlist.err_console", mock_err_console)
    return mock_console, mock_err_console
