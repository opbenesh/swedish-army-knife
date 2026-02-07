import time
import pytest
from typer.testing import CliRunner
from unittest.mock import MagicMock, patch
from src.main import app

runner = CliRunner()

def test_search_parallel_performance(mocker):
    """
    Verify that the search command uses parallel execution.
    We mock a 50ms latency per request.
    With 50 items:
    - Sequential: ~2.5 seconds (50 * 0.05)
    - Parallel (10 workers): ~0.25 seconds (5 * 0.05)
    """
    # Mock data
    lines = [f"Artist{i} - Title{i}" for i in range(50)]
    input_data = "\n".join(lines)

    # Mock Spotify client
    mock_sp = MagicMock()

    def slow_search(q, type, limit):
        time.sleep(0.05) # Simulate 50ms latency
        # Extract index from q to verify correctness if needed
        # q format: 'artist:Artist{i} track:Title{i}'
        try:
            # We trust the input format because we generated it
            idx = q.split("track:Title")[1]
            return {
                'tracks': {
                    'items': [{
                        'uri': f"spotify:track:{idx}",
                        'id': f"{idx}",
                        'name': f"Title{idx}",
                        'artists': [{'name': f"Artist{idx}"}]
                    }]
                }
            }
        except:
            return {'tracks': {'items': []}}

    mock_sp.search.side_effect = slow_search

    # Patch get_spotify to return our mock
    mocker.patch("src.main.get_spotify", return_value=mock_sp)

    start_time = time.time()
    result = runner.invoke(app, ["playlist", "search"], input=input_data)
    end_time = time.time()

    duration = end_time - start_time
    print(f"\nExecution time for 50 items: {duration:.2f} seconds")

    assert result.exit_code == 0

    # Verify output count
    output_lines = [l for l in result.stdout.split("\n") if l.strip()]
    assert len(output_lines) == 50

    # Assert performance: Should be significantly faster than sequential (2.5s)
    # We allow some overhead, but 1.0s is a very safe upper bound for 0.25s expected.
    assert duration < 1.0, f"Search took {duration}s, expected < 1.0s (Parallel execution failed?)"
