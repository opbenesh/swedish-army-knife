from typing import List, Generator, Optional, Set
import spotipy
import concurrent.futures
from rich.console import Console
from rapidfuzz import process, fuzz

console = Console()
err_console = Console(stderr=True)

def get_playlist_track_uris(sp: spotipy.Spotify, playlist_id: str) -> Set[str]:
    """Fetch all track URIs from a playlist, handling pagination."""
    track_uris = set()
    results = sp.playlist_tracks(playlist_id)
    while results:
        for item in results['items']:
            track = item['track']
            if track and track.get('uri'):
                track_uris.add(track['uri'])
        results = sp.next(results) if results.get('next') else None
    return track_uris

def normalize_track_uri(track_id_or_uri: str) -> str:
    """Ensure a track string is a full Spotify URI."""
    if track_id_or_uri.startswith("spotify:track:"):
        return track_id_or_uri
    return f"spotify:track:{track_id_or_uri}"

def move_tracks(sp: spotipy.Spotify, track_uris: List[str], source_id: str, dest_id: str, strict: bool = False):
    """
    Move tracks from source playlist to destination playlist.
    Uses batching to minimize API calls (Spotify limit: 100 per call).

    If strict is True, only moves tracks that actually exist in the source playlist.
    """
    if not track_uris:
        return

    tracks_to_move = track_uris
    if strict:
        source_uris = get_playlist_track_uris(sp, source_id)

        # Filter tracks: normalize both for comparison
        filtered_tracks = []
        skipped_count = 0
        for track in track_uris:
            if normalize_track_uri(track) in source_uris:
                filtered_tracks.append(track)
            else:
                skipped_count += 1

        if skipped_count > 0:
            console.print(f"[yellow]Strict Mode: Skipped {skipped_count} tracks not found in source playlist.[/]")

        tracks_to_move = filtered_tracks

    if not tracks_to_move:
        console.print("[yellow]No tracks to move after filtering.[/]")
        return

    # Batching logic
    batch_size = 100
    for i in range(0, len(tracks_to_move), batch_size):
        batch = tracks_to_move[i:i + batch_size]
        
        # 1. Add to destination
        sp.playlist_add_items(dest_id, batch)
        
        # 2. Remove from source
        # Note: We use playlist_remove_all_occurrences_of_items to be efficient
        sp.playlist_remove_all_occurrences_of_items(source_id, batch)
        
    console.print(f"[green]Successfully moved {len(tracks_to_move)} tracks.[/]")

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
def _search_worker(sp: spotipy.Spotify, line: str) -> Optional[dict]:
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

def search_tracks(sp: spotipy.Spotify, lines: List[str], playlist_id: Optional[str] = None) -> Generator[Optional[dict], None, None]:
    """
    Search for tracks based on "Artist - Title" lines.
    If playlist_id is provided, restricts search to that playlist using fuzzy matching.
    Otherwise, uses global Spotify search with ThreadPoolExecutor.
    """
    if playlist_id:
        # Fetch all tracks from playlist
        playlist_tracks = []
        try:
            results = sp.playlist_tracks(playlist_id)
            while results:
                for item in results['items']:
                    if item.get('track'):
                        playlist_tracks.append(item['track'])
                results = sp.next(results) if results.get('next') else None
        except Exception as e:
            err_console.print(f"[bold red]Error fetching playlist:[/] {str(e)}")
            for _ in lines:
                yield None
            return

        if not playlist_tracks:
            err_console.print(f"[yellow]Playlist {playlist_id} is empty or not found.[/]")
            for _ in lines:
                yield None
            return

        # Prepare searchable strings
        # We'll map "Artist - Title" string back to the track object
        track_map = {}
        search_choices = []
        for track in playlist_tracks:
            artists = ', '.join([a['name'] for a in track['artists']])
            search_str = f"{artists} - {track['name']}"
            search_choices.append(search_str)
            # Handle duplicates by keeping the first one or similar?
            # For now, just map search_str to track
            if search_str not in track_map:
                track_map[search_str] = track

        for line in lines:
            line = line.strip()
            if not line:
                yield None
                continue

            # Use fuzzy matching
            match = process.extractOne(line, search_choices, scorer=fuzz.WRatio)
            if match and match[1] > 60: # Threshold of 60
                yield track_map[match[0]]
            else:
                err_console.print(f"[red]Not found in playlist:[/] {line}")
                yield None
    else:
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            # Submit all tasks and preserve order
            futures = [executor.submit(_search_worker, sp, line) for line in lines]

            for future in futures:
                yield future.result()
