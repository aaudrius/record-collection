import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

def get_spotify_client():
    spotify_client_credentials_manager = SpotifyClientCredentials(
        client_id='0b49e29110a94a09b112f3002b759d4c',
        client_secret='2b0b8f5b97e14c6abc466aa649bf0427'
    )
    return spotipy.Spotify(client_credentials_manager=spotify_client_credentials_manager)

def search_spotify_album(spotify_client, album_name, artist_name):
    results = spotify_client.search(q=f'album:{album_name} artist:{artist_name}', type='album')
    items = results['albums']['items']
    if items:
        return items[0]['id']
    return None
