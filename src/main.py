import typer
import sys
from pathlib import Path
from typing import Optional
from rich.console import Console
from .spotify_client import get_spotify
from .commands.playlist import move_tracks as do_move_tracks


app = typer.Typer(help="Swedish Army Knife for Spotify actions.")
playlist_app = typer.Typer(help="Playlist management commands.")
app.add_typer(playlist_app, name="playlist")

console = Console()
err_console = Console(stderr=True)

def is_interactive():
    return sys.stdin.isatty()

@app.command()
def status():
    """Check Spotify connection status."""
    try:
        sp = get_spotify()
        user = sp.current_user()
        console.print(f"[bold green]Connected![/] Logged in as: [cyan]{user['display_name']}[/] ({user['id']})")
    except Exception as e:
        err_console.print(f"[bold red]Status Failed:[/] {str(e)}")

@playlist_app.command(name="move")
def move(
    tracks_file: Optional[Path] = typer.Option(None, "--file", "-f", help="File containing track URIs/IDs, one per line. If not provided, reads from stdin."),
    source: str = typer.Option(..., "--from", "-s", help="Source playlist ID."),
    dest: str = typer.Option(..., "--to", "-d", help="Destination playlist ID.")
):
    """Move tracks from one playlist to another. Reads track URIs from file or stdin."""
    if tracks_file:
        if not tracks_file.exists():
            err_console.print(f"[bold red]Error:[/] File {tracks_file} does not exist.")
            raise typer.Exit(1)
        with open(tracks_file, "r") as f:
            tracks = [line.strip() for line in f if line.strip()]
    else:
        # Read from stdin
        if is_interactive():
            err_console.print("[bold red]Error:[/] No input provided. Use --file or pipe track URIs via stdin.")
            raise typer.Exit(1)
        tracks = [line.strip() for line in sys.stdin if line.strip()]
        
    if not tracks:
        console.print("[yellow]No tracks found.[/]")
        return
        
    try:
        sp = get_spotify()
        do_move_tracks(sp, tracks, source, dest)
    except Exception as e:
        err_console.print(f"[bold red]Move Failed:[/] {str(e)}")

@playlist_app.command(name="search")
def search():
    """Search for tracks and output their URIs. Reads 'Artist - Title' lines from stdin."""
    if is_interactive():
        err_console.print("[bold red]Error:[/] No input provided. Pipe 'Artist - Title' lines via stdin.")
        raise typer.Exit(1)
    
    try:
        sp = get_spotify()
    except Exception as e:
        err_console.print(f"[bold red]Connection Failed:[/] {str(e)}")
        raise typer.Exit(1)
    
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        
        # Parse "Artist - Title" format
        if " - " not in line:
            err_console.print(f"[yellow]Skipping invalid format:[/] {line}")
            continue
            
        artist, title = line.split(" - ", 1)
        result = sp.search(q=f'artist:{artist} track:{title}', type='track', limit=1)
        
        if result['tracks']['items']:
            uri = result['tracks']['items'][0]['uri']
            print(uri)  # Output to stdout for piping
        else:
            err_console.print(f"[red]Not found:[/] {artist} - {title}")

if __name__ == "__main__":
    app()
