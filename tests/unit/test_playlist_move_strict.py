import pytest
from unittest.mock import MagicMock
from src.commands.playlist import move_tracks

def test_move_tracks_strict_mode(mocker):
    sp = MagicMock()

    # Source playlist has tracks 1 and 2
    # We want to move tracks 2 and 3
    # Track 3 should be skipped because it's not in the source playlist

    source_id = "source_id"
    dest_id = "dest_id"
    input_tracks = ["spotify:track:2", "spotify:track:3"]

    # Mocking playlist_tracks
    sp.playlist_tracks.return_value = {
        'items': [
            {'track': {'uri': 'spotify:track:1'}},
            {'track': {'uri': 'spotify:track:2'}}
        ],
        'next': None
    }

    # Execute move with strict=True
    move_tracks(sp, input_tracks, source_id, dest_id, strict=True)

    # Should only add track 2 to destination
    sp.playlist_add_items.assert_called_once_with(dest_id, ["spotify:track:2"])

    # Should only remove track 2 from source
    sp.playlist_remove_all_occurrences_of_items.assert_called_once_with(source_id, ["spotify:track:2"])

def test_move_tracks_non_strict_mode(mocker):
    sp = MagicMock()

    source_id = "source_id"
    dest_id = "dest_id"
    input_tracks = ["spotify:track:2", "spotify:track:3"]

    # Execute move with strict=False (default)
    move_tracks(sp, input_tracks, source_id, dest_id, strict=False)

    # Should add both to destination
    sp.playlist_add_items.assert_called_once_with(dest_id, ["spotify:track:2", "spotify:track:3"])

    # Should try to remove both from source
    sp.playlist_remove_all_occurrences_of_items.assert_called_once_with(source_id, ["spotify:track:2", "spotify:track:3"])

def test_move_tracks_strict_mode_with_ids(mocker):
    sp = MagicMock()

    # Test that it handles IDs by normalizing them to URIs
    source_id = "source_id"
    dest_id = "dest_id"
    input_tracks = ["track2", "track3"]

    # Mocking playlist_tracks returns URIs
    sp.playlist_tracks.return_value = {
        'items': [
            {'track': {'uri': 'spotify:track:track1'}},
            {'track': {'uri': 'spotify:track:track2'}}
        ],
        'next': None
    }

    # Execute move with strict=True
    move_tracks(sp, input_tracks, source_id, dest_id, strict=True)

    # Should only add track 2 to destination
    sp.playlist_add_items.assert_called_once_with(dest_id, ["track2"])

    # Should only remove track 2 from source
    sp.playlist_remove_all_occurrences_of_items.assert_called_once_with(source_id, ["track2"])
