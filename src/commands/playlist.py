from typing import List, Optional
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

def add_tracks(sp: spotipy.Spotify, track_uris: List[str], playlist_id: str):
    """
    Add tracks to a playlist.
    Uses batching to minimize API calls (Spotify limit: 100 per call).
    """
    if not track_uris:
        return

    batch_size = 100
    for i in range(0, len(track_uris), batch_size):
        batch = track_uris[i:i + batch_size]
        sp.playlist_add_items(playlist_id, batch)
        
    console.print(f"[green]Successfully added {len(track_uris)} tracks.[/]")

def create_playlist(sp: spotipy.Spotify, name: str) -> str:
    """
    Create a new playlist for the current user and return its URI.
    """
    user = sp.current_user()
    playlist = sp.user_playlist_create(user['id'], name)
    return playlist['uri']

def find_playlist(sp: spotipy.Spotify, name: str) -> Optional[str]:
    """
    Find a playlist ID by its name.
    """
    results = sp.current_user_playlists()
    while results:
        for item in results['items']:
            if item['name'] == name:
                return item['id']
        if results.get('next'):
            results = sp.next(results)
        else:
            results = None
    return None
