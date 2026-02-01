import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class Settings:
    @property
    def SPOTIPY_CLIENT_ID(self):
        return os.getenv("SPOTIPY_CLIENT_ID")

    @property
    def SPOTIPY_CLIENT_SECRET(self):
        return os.getenv("SPOTIPY_CLIENT_SECRET")

    @property
    def SPOTIPY_REDIRECT_URI(self):
        return os.getenv("SPOTIPY_REDIRECT_URI", "http://localhost:8888/callback")
    
    @property
    def is_spotify_configured(self) -> bool:
        return all([self.SPOTIPY_CLIENT_ID, self.SPOTIPY_CLIENT_SECRET])

settings = Settings()
