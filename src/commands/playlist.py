from typing import List
import spotipy
from rich.console import Console

console = Console()

def move_tracks(sp: spotipy.Spotify, track_uris: List[str], source_id: str, dest_id: str):
    """
    Move tracks from source playlist to destination playlist.
    Uses batching to minimize API calls (Spotify limit: 100 per call).
    """
    if not track_uris:
        return

    # Batching logic
    batch_size = 100
    for i in range(0, len(track_uris), batch_size):
        batch = track_uris[i:i + batch_size]
        
        # 1. Add to destination
        sp.playlist_add_items(dest_id, batch)
        
        # 2. Remove from source
        # Note: We use playlist_remove_all_occurrences_of_items to be efficient
        sp.playlist_remove_all_occurrences_of_items(source_id, batch)
        
    console.print(f"[green]Successfully moved {len(track_uris)} tracks.[/]")
