import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
from menu import menu



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

        menu(sp)

        # open(r"D:\WSEI 2 year\SEM4\Python\Profiler\DB\samurai champloo music record departure.csv")

    except Exception as e:
        print(f"Wystąpił błąd: {e}")

########### Przeczytać o tym w notatkach ###########
if __name__ == "__main__":
    main()
####################################################
