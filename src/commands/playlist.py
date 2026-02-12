from typing import List, Generator, Optional, Any
import spotipy
import concurrent.futures
from rich.console import Console

console = Console()
err_console = Console(stderr=True)

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

def get_playlist_tracks(sp: spotipy.Spotify, playlist_id: str) -> Generator[dict, None, None]:
    """
    Yields tracks from a playlist.
    Handles pagination automatically.
    """
    results = sp.playlist_tracks(playlist_id)
    while results:
        for item in results['items']:
            if item['track']:  # Can be None for local/unavailable tracks
                yield item['track']
        results = sp.next(results) if results.get('next') else None

def _search_worker(sp: spotipy.Spotify, line: str) -> Optional[dict]:
    """
    Helper function to search for a single track.
    Returns track dict or None.
    """
    line = line.strip()
    if not line:
        return None

    # Parse "Artist - Title" format
    if " - " not in line:
        err_console.print(f"[yellow]Skipping invalid format:[/] {line}")
        return None

    artist, title = line.split(" - ", 1)
    try:
        result = sp.search(q=f'artist:{artist} track:{title}', type='track', limit=1)

        if result['tracks']['items']:
            return result['tracks']['items'][0]
        else:
            err_console.print(f"[red]Not found:[/] {artist} - {title}")
            return None
    except Exception as e:
        err_console.print(f"[red]Error searching for:[/] {line} - {str(e)}")
        return None

def search_tracks(sp: spotipy.Spotify, lines: List[str]) -> Generator[Optional[dict], None, None]:
    """
    Search for tracks in parallel.
    Yields found track objects (or None) in order.
    """
    # Use ThreadPoolExecutor for parallel processing
    # Limit workers to avoid rate limits
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        # Submit all tasks and preserve order
        futures = [executor.submit(_search_worker, sp, line) for line in lines]

        for future in futures:
            yield future.result()
