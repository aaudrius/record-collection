import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

load_dotenv()

def get_spotify_client():
    spotify_client_credentials_manager = SpotifyClientCredentials(
        client_id = os.getenv('SPOTIFY_CLIENT_ID'),
        client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
    )
    return spotipy.Spotify(client_credentials_manager=spotify_client_credentials_manager)

def search_spotify_album(spotify_client, album_name, artist_name):
    results = spotify_client.search(q=f'album:{album_name} artist:{artist_name}', type='album')
    items = results['albums']['items']
    if items:
        return items[0]['id']
    return None
