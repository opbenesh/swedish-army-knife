import spotipy
from spotipy.oauth2 import SpotifyOAuth
from .config import settings
import sys
from rich.console import Console

console = Console()

class SpotifyClient:
    def __init__(self, scope: str = "playlist-modify-public playlist-modify-private"):
        if not settings.is_spotify_configured:
            console.print("[bold red]Error:[/] Spotify credentials not found in .env file.")
            console.print("Please update .env with SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET.")
            sys.exit(1)
            
        self.sp_oauth = SpotifyOAuth(
            client_id=settings.SPOTIPY_CLIENT_ID,
            client_secret=settings.SPOTIPY_CLIENT_SECRET,
            redirect_uri=settings.SPOTIPY_REDIRECT_URI,
            scope=scope,
            cache_path=".cache"
        )
        
    def get_client(self) -> spotipy.Spotify:
        token_info = self.sp_oauth.get_cached_token()
        
        if not token_info:
            console.print("[yellow]Initial authentication required. Opening browser...[/]")
            auth_url = self.sp_oauth.get_authorize_url()
            # In a CLI, SpotifyOAuth usually handles opening the browser automatically
            # if we use certain methods, but we can also get the client directly:
            return spotipy.Spotify(auth_manager=self.sp_oauth)
            
        return spotipy.Spotify(auth_manager=self.sp_oauth)

# Shared instance helper
def get_spotify() -> spotipy.Spotify:
    return SpotifyClient().get_client()
