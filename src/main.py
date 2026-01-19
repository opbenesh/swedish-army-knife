import typer
from pathlib import Path
from rich.console import Console
from .spotify_client import get_spotify
from .commands.playlist import move_tracks as do_move_tracks


app = typer.Typer(help="Swedish Army Knife for Spotify actions.")
playlist_app = typer.Typer(help="Playlist management commands.")
app.add_typer(playlist_app, name="playlist")

console = Console()

@app.command()
def status():
    """Check Spotify connection status."""
    try:
        sp = get_spotify()
        user = sp.current_user()
        console.print(f"[bold green]Connected![/] Logged in as: [cyan]{user['display_name']}[/] ({user['id']})")
    except Exception as e:
        console.print(f"[bold red]Status Failed:[/] {str(e)}")

@playlist_app.command(name="move")
def move(
    tracks_file: Path = typer.Option(..., "--file", "-f", help="File containing track URIs/IDs, one per line."),
    source: str = typer.Option(..., "--from", "-s", help="Source playlist ID."),
    dest: str = typer.Option(..., "--to", "-d", help="Destination playlist ID.")
):
    """Move tracks from one playlist to another."""
    if not tracks_file.exists():
        console.print(f"[bold red]Error:[/] File {tracks_file} does not exist.")
        raise typer.Exit(1)
        
    with open(tracks_file, "r") as f:
        # Filter out empty lines and whitespace
        tracks = [line.strip() for line in f if line.strip()]
        
    if not tracks:
        console.print("[yellow]No tracks found in file.[/]")
        return
        
    try:
        sp = get_spotify()
        do_move_tracks(sp, tracks, source, dest)
    except Exception as e:
        console.print(f"[bold red]Move Failed:[/] {str(e)}")

if __name__ == "__main__":
    app()
