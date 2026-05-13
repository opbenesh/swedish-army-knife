import sys
from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console

from .commands.playlist import (
    add_tracks as do_add_tracks,
)
from .commands.playlist import (
    create_playlist as do_create_playlist,
)
from .commands.playlist import (
    find_playlist as do_find_playlist,
)
from .commands.playlist import (
    move_tracks as do_move_tracks,
)
from .commands.playlist import (
    search_tracks as do_search_tracks,
)
from .spotify_client import get_spotify
from .utils import format_track, parse_playlist_id

app = typer.Typer(help="Swedish Army Knife for Spotify actions.")
playlist_app = typer.Typer(help="Playlist management commands.")
app.add_typer(playlist_app, name="playlist")

console = Console()
err_console = Console(stderr=True)


def is_interactive() -> bool:
    return sys.stdin.isatty()


def _read_tracks(tracks_file: Optional[Path]) -> List[str]:
    """Read track URIs from a file or stdin. Exits with error if no input is available."""
    if tracks_file:
        if not tracks_file.exists():
            err_console.print(f"[bold red]Error:[/] File {tracks_file} does not exist.")
            raise typer.Exit(1)
        with open(tracks_file) as f:
            return [line.strip() for line in f if line.strip()]
    else:
        if is_interactive():
            err_console.print(
                "[bold red]Error:[/] No input provided. Use --file or pipe track URIs via stdin."
            )
            raise typer.Exit(1)
        return [line.strip() for line in sys.stdin if line.strip()]


@app.command()
def status():
    """Check Spotify connection status."""
    try:
        sp = get_spotify()
        user = sp.current_user()
        name, uid = user["display_name"], user["id"]
        console.print(f"[bold green]Connected![/] Logged in as: [cyan]{name}[/] ({uid})")
    except Exception as e:
        err_console.print(f"[bold red]Status Failed:[/] {str(e)}")
        raise typer.Exit(1)


@playlist_app.command(name="create")
def create(name: str = typer.Option(..., "--name", "-n", help="Name of the new playlist.")):
    """Create a new playlist."""
    try:
        sp = get_spotify()
        uri = do_create_playlist(sp, name)
        console.print(uri)
    except Exception as e:
        err_console.print(f"[bold red]Create Failed:[/] {str(e)}")
        raise typer.Exit(1)


@playlist_app.command(name="move")
def move(
    tracks_file: Optional[Path] = typer.Option(
        None, "--file", "-f", help="File with track URIs/IDs, one per line. Defaults to stdin."
    ),
    source: str = typer.Option(..., "--from", "-s", help="Source playlist ID."),
    dest: str = typer.Option(..., "--to", "-d", help="Destination playlist ID."),
    strict: bool = typer.Option(
        False, "--strict", help="Only move tracks present in the source playlist."
    ),
):
    """Move tracks from one playlist to another. Reads track URIs from file or stdin.

    If --strict is used, it verifies tracks exist in the source playlist before moving.
    """
    tracks = _read_tracks(tracks_file)

    if not tracks:
        console.print("[yellow]No tracks found.[/]")
        return

    try:
        sp = get_spotify()
        do_move_tracks(sp, tracks, source, dest, strict=strict)
    except Exception as e:
        err_console.print(f"[bold red]Move Failed:[/] {str(e)}")
        raise typer.Exit(1)


@playlist_app.command(name="search")
def search(
    output: str = typer.Option("uri", "--output", "-o", help="Output: uri, id, text, json"),
    format_opt: Optional[str] = typer.Option(None, "--format", help="Alias for --output"),
    in_playlist: Optional[str] = typer.Option(
        None, "--in-playlist", help="Restrict search to a specific playlist ID."
    ),
):
    """Search for tracks and output URIs. Reads 'Artist - Title' lines from stdin."""
    if format_opt:
        output = format_opt

    if is_interactive():
        err_console.print("[bold red]Error:[/] No input provided. Pipe 'Artist - Title' lines via stdin.")  # noqa: E501
        raise typer.Exit(1)

    try:
        sp = get_spotify()
    except Exception as e:
        err_console.print(f"[bold red]Connection Failed:[/] {str(e)}")
        raise typer.Exit(1)

    lines = sys.stdin.readlines()

    for track in do_search_tracks(sp, lines, playlist_id=in_playlist):
        if track:
            print(format_track(track, output))


@playlist_app.command(name="list")
def list_tracks(
    url: Optional[str] = typer.Option(None, "--url", "-u", help="Spotify playlist URL"),
    playlist_id: Optional[str] = typer.Option(None, "--id", "-i", help="Spotify playlist ID"),
    output: str = typer.Option("text", "--output", "-o", help="Output: text, uri, id"),
):
    """List tracks from a playlist. Default output is 'Artist - Title'."""
    if url:
        playlist_id = parse_playlist_id(url)
        if not playlist_id:
            err_console.print("[bold red]Error:[/] Invalid playlist URL")
            raise typer.Exit(1)

    if not playlist_id:
        err_console.print("[bold red]Error:[/] Provide --url or --id")
        raise typer.Exit(1)

    try:
        sp = get_spotify()
        results = sp.playlist_tracks(playlist_id)
        while results:
            for item in results["items"]:
                track = item["track"]
                if track:  # Can be None for local/unavailable tracks
                    print(format_track(track, output))
            results = sp.next(results) if results.get("next") else None
    except Exception as e:
        err_console.print(f"[bold red]Error:[/] {str(e)}")
        raise typer.Exit(1)


@playlist_app.command(name="add")
def add_tracks_to_playlist(
    tracks_file: Optional[Path] = typer.Option(
        None, "--file", "-f", help="File with track URIs/IDs, one per line. Defaults to stdin."
    ),
    url: Optional[str] = typer.Option(None, "--url", "-u", help="Spotify playlist URL"),
    playlist_id: Optional[str] = typer.Option(None, "--id", "-i", help="Spotify playlist ID"),
):
    """Add tracks to a playlist. Reads track URIs from file or stdin."""
    if url:
        playlist_id = parse_playlist_id(url)
        if not playlist_id:
            err_console.print("[bold red]Error:[/] Invalid playlist URL")
            raise typer.Exit(1)

    if not playlist_id:
        err_console.print("[bold red]Error:[/] Provide --url or --id")
        raise typer.Exit(1)

    tracks = _read_tracks(tracks_file)

    if not tracks:
        console.print("[yellow]No tracks found.[/]")
        return

    try:
        sp = get_spotify()
        do_add_tracks(sp, tracks, playlist_id)
    except Exception as e:
        err_console.print(f"[bold red]Add Failed:[/] {str(e)}")
        raise typer.Exit(1)


@playlist_app.command(name="find")
def find_playlist(name: str = typer.Argument(..., help="The name of the playlist to find.")):
    """Find a playlist ID by its name."""
    try:
        sp = get_spotify()
        playlist_id = do_find_playlist(sp, name)
        if playlist_id:
            console.print(playlist_id)
        else:
            err_console.print(f"[bold red]Error:[/] Playlist '{name}' not found.")
            raise typer.Exit(1)
    except typer.Exit:
        raise
    except Exception as e:
        err_console.print(f"[bold red]Find Failed:[/] {str(e)}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
