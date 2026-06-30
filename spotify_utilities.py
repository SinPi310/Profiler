import os
import csv
import spotipy
import pandas as pd
from datetime import datetime

def album_download(sp: spotipy.Spotify, album_url: str) -> list:
    print("+---------------------------------------+")
    print("|       Downloading tracks...           |")

    result = sp.album_tracks(album_url)
    tracks = result['items']
    tracks_list = []

    while result['next']:
        result = sp.next(result)
        tracks.extend(result['items'])

    for track in tracks:
        track_info = {
            'id': track['id'],
            'title': track['name'],
            'artist': ', '.join([artist['name'] for artist in track['artists']]),
            'disc_number': track['disc_number'],
            'track_number': track['track_number'],
            'duration_ms': track['duration_ms'],
            'rate': 0,
            'superstar': False,
            'rate_date': ''
        }
        tracks_list.append(track_info)

    print(f"|         Downloaded {len(tracks_list)} tracks!         |")
    print("+---------------------------------------+")
    return tracks_list

def save_to_csv(tracks_list: list, album_name: str) -> str:
    os.makedirs("DB", exist_ok=True)
    album_name_formate = "".join([c for c in album_name if c.isalnum() or c in " _-"]).rstrip()
    path = os.path.join("DB", f"{album_name_formate}.csv")

    df = pd.DataFrame(tracks_list)
    df.to_csv(path, index=False, encoding='utf-8-sig')

    return path

def open_csv_file(file_path: str) -> list:
    with open(file_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)

        file_name = os.path.splitext(os.path.basename(file_path))[0]
        print(f"\n{file_name}")

        for track in reader:
            special = "*" if track['superstar'] else ""
            print(f"{track['track_number']}. {track['title']} [{track['artist']}]   {track['rate']}{special}")

def rate_tracks(track_list: list, album_name: str) -> list:
    print("\nHi, \n pleace tipe rate, between 1 and 10, after the track name. \n PS. You can also tipe [ * ] for super ultra grate tracks")
    print("")
    print(album_name)

    for track in track_list:
        while True:
            user_rate = input(f" {track['track_number']}. {track['title']} [{track['artist']}] -> rate: ").strip()

            is_superstar = '*' in user_rate
            user_rate_number = user_rate.replace('*', '')

            try:
                user_rate_int = int(user_rate_number)

                if 1 <= user_rate_int <= 10:
                    track['rate'] = user_rate_int
                    track['superstar'] = is_superstar
                    track['rate_date'] = datetime.now().strftime("%Y-%m-%d")
                    break

                else:
                    print("Rate must be between 1 and 10!!!")

            except ValueError:
                print("Valid user input!!!")

    return track_list


def format_ms(ms: int) -> str:
    minutes = int((ms / (1000 * 60)) % 60)
    seconds = int((ms / 1000) % 60)
    return f"{minutes:02d}:{seconds:02d}"
