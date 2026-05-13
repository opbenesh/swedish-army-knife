import sys

import spotipy
from rich.console import Console
from spotipy.oauth2 import SpotifyOAuth

from .config import settings

console = Console()
err_console = Console(stderr=True)

class SpotifyClient:
    _DEFAULT_SCOPE = (
        "playlist-modify-public playlist-modify-private"
        " user-library-read user-library-modify"
    )

    def __init__(self, scope: str = _DEFAULT_SCOPE):
        if not settings.is_spotify_configured:
            err_console.print("[bold red]Error:[/] Spotify credentials not found in .env file.")
            err_console.print("Set SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET in .env.")
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
            auth_url = self.sp_oauth.get_authorize_url()
            console.print("[yellow]Open this URL in your browser to authenticate:[/]")
            console.print(f"\n{auth_url}\n")
            console.print("[yellow]After authorizing, paste the full redirect URL here[/]")
            console.print("[dim](even if the browser shows an error, the URL contains the code)[/]")
            redirect_url = input("Redirect URL: ").strip()
            code = self.sp_oauth.parse_response_code(redirect_url)
            self.sp_oauth.get_access_token(code, as_dict=False, check_cache=False)

        return spotipy.Spotify(auth_manager=self.sp_oauth)

# Shared instance helper
def get_spotify() -> spotipy.Spotify:
    return SpotifyClient().get_client()
