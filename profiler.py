import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv

def format_ms(ms: int) -> str:
    """Konwertuje milisekundy na format MM:SS."""
    seconds = int((ms / 1000) % 60)
    minutes = int((ms / (1000 * 60)) % 60)
    return f"{minutes:02d}:{seconds:02d}"


# Zmieniona nazwa funkcji dla jasności
def download_album(sp: spotipy.Spotify, album_url: str) -> list:
    """
    Pobiera listę utworów z podanego linku do albumu.
    Zwraca listę słowników z informacjami o piosenkach.
    """
    print("+---------------------------------------+")
    print("|      Pobieram utwory z albumu...      |")

    # Spotify API zwraca utwory "paczkami", pobieramy pierwszą paczkę
    wyniki = sp.album_tracks(album_url)
    utwory = wyniki['items']  # To już jest lista obiektów utworów

    tracks_list = []

    # Przechodzimy przez każdy utwór na albumie
    # UWAGA: Struktura odpowiedzi dla albumu jest inna niż dla playlisty.
    # Obiekt `track` nie jest zagnieżdżony w `element['track']`.
    for track in utwory:
        # Czasem piosenki mogą być niedostępne, więc zabezpieczamy się 'if track:'
        if track:
            artist = "Unknown"

            if 'artists' in track and track['artists']:
                artist = ", ".join([a['name'] for a in track['artists']])

            utwor_info = {
                'id': track['id'],
                'title': track['name'],
                'artist': artist,
                'duration_ms': track['duration_ms']
            }
            tracks_list.append(utwor_info)

    print(f"|          Pobrano {len(tracks_list)} utworów!          |")
    print("+---------------------------------------+")
    return tracks_list

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
        album_id = '1Uwd64LlYKeBEVpZ4civSQ'
        album_data = sp.album(album_id)
        tracks_list = download_album(sp, album_id)

        # 4. DISPLAY tytułu albumu
        print(f"\n{album_data['name']}")
        
        i = 1
        for track in tracks_list:
            # Używamy naszej nowej funkcji do formatowania czasu
            czas_trwania = format_ms(track['duration_ms'])
            print(f" {i}. {track['title']} *[{track['artist']}] [{czas_trwania}]")
            i += 1

    except Exception as e:
        print(f"Wystąpił błąd: {e}")

########### Przeczytać o tym w notatkach ###########
if __name__ == "__main__":
    main()
####################################################
