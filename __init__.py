import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
from spotify_utilities import album_download as download, open_csv_file as open, save_to_csv as save, rate_tracks as rate



def main():
    load_dotenv()
    client_id = os.getenv("SPOTIPY_CLIENT_ID")
    client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")

    if not client_id or not client_secret or client_id == 'TWOJ_CLIENT_ID':
        print("!!!Valid API KEY!!!")
        return

    try:
        # 1. Token autoryzacyjny
        auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
        sp = spotipy.Spotify(auth_manager=auth_manager)

        link = input("Pass your spotify album link: ").strip()

        album_data = sp.album(link)
        album_name = album_data['name']

        row_album_data = download(sp, link)

        rated_album = rate(row_album_data, album_name)

        path = save(rated_album, album_name)

        # open(r"D:\WSEI 2 year\SEM4\Python\Profiler\DB\samurai champloo music record departure.csv")

    except Exception as e:
        print(f"Wystąpił błąd: {e}")

########### Przeczytać o tym w notatkach ###########
if __name__ == "__main__":
    main()
####################################################
