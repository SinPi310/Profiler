import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
from spotify_utilities import album_download, format_ms

def main():
    load_dotenv()

    client_id = os.getenv("SPOTIPY_CLIENT_ID")
    client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")

    if not client_id or not client_secret or client_id == 'TWOJ_CLIENT_ID':
        print("!!!Błąd z kluczami API!!!")
        return

    try:
        # 1. LOGOWANIE
        auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
        sp = spotipy.Spotify(auth_manager=auth_manager)

        # 2. POBRANIE albumu i utworów
        album_id = 'https://open.spotify.com/album/0rXkEiNBQAspPBy0ai23F9'
        album_data = sp.album(album_id)
        tracks_list = album_download(sp, album_id)

        # 4. DISPLAY tytułu albumu
        print(f"\n{album_data['name']}")
        print(f"{album_data['release_date']}")
        print()

        for track in tracks_list:
            duration_formatted = format_ms(track['duration_ms'])
            print(f" {track['track_number']}. {track['title']} [{duration_formatted}]")

    except Exception as e:
        print(f"Wystąpił błąd: {e}")

########### Przeczytać o tym w notatkach ###########
if __name__ == "__main__":
    main()
####################################################
