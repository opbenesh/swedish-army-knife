import pytest
from unittest.mock import MagicMock
from src.commands.playlist import move_tracks

def test_move_tracks_batching(mocker):
    # Mock Spotify client
    sp = MagicMock()
    
    # Track list of 150 items to test batching (max 100 per call)
    tracks = [f"spotify:track:{i}" for i in range(150)]
    source_id = "source_playlist_id"
    dest_id = "dest_playlist_id"
    
    # Execute move
    move_tracks(sp, tracks, source_id, dest_id)
    
    # Verify dest additions: Should call playlist_add_items twice
    # Batch 1: 100, Batch 2: 50
    assert sp.playlist_add_items.call_count == 2
    
    # Verify source removals: Should call playlist_remove_all_occurrences_of_items twice
    assert sp.playlist_remove_all_occurrences_of_items.call_count == 2
    
def test_move_tracks_empty(mocker):
    sp = MagicMock()
    move_tracks(sp, [], "src", "dest")
    
    sp.playlist_add_items.assert_not_called()
    sp.playlist_remove_all_occurrences_of_items.assert_not_called()
