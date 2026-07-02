import csv
import os
from datetime import datetime

import pandas as pd

from analysis import format_ms


def normalize_file_name(name: str) -> str:
    return "".join([c for c in name if c.isalnum() or c in " _-"]).rstrip()


def get_album_csv_path(album_name: str, artist_name: str) -> str:
    artist_name_formate = normalize_file_name(artist_name)
    album_name_formate = normalize_file_name(album_name)

    album_directory = os.path.join("db", "albums", artist_name_formate)
    os.makedirs(album_directory, exist_ok=True)

    return os.path.join(album_directory, f"{album_name_formate}.csv")


def album_csv_exists(album_name: str, artist_name: str) -> bool:
    path = get_album_csv_path(album_name, artist_name)
    return os.path.exists(path)


def save_to_csv(tracks_list: list, album_name: str, artist_name: str) -> str:
    path = get_album_csv_path(album_name, artist_name)

    df = pd.DataFrame(tracks_list)
    df.to_csv(path, index=False, encoding="utf-8-sig")

    return path


def get_artist_album_list_path(artist_name: str) -> str:
    artist_name_formate = normalize_file_name(artist_name)
    os.makedirs(os.path.join("db", "artists_albums"), exist_ok=True)
    return os.path.join("db", "artists_albums", f"{artist_name_formate}_album_list.csv")


def get_artists_csv_path() -> str:
    os.makedirs("db", exist_ok=True)
    return os.path.join("db", "artists.csv")


def save_artist_if_missing(artist_name: str, artist_id: str = "") -> str:
    path = get_artists_csv_path()
    albums_cache_path = get_artist_album_list_path(artist_name)

    new_artist = {
        "artist_name": artist_name,
        "artist_id": artist_id,
        "albums_cache_path": albums_cache_path,
        "created_at": datetime.now().strftime("%Y-%m-%d"),
    }

    if os.path.exists(path):
        df = pd.read_csv(path)

        if "artist_name" in df.columns and artist_name in df["artist_name"].astype(str).values:
            return path

        df = pd.concat([df, pd.DataFrame([new_artist])], ignore_index=True)
    else:
        df = pd.DataFrame([new_artist])

    df.to_csv(path, index=False, encoding="utf-8-sig")
    return path


def save_artist_album_list(albums_list: list, artist_name: str) -> str:
    path = get_artist_album_list_path(artist_name)
    df = pd.DataFrame(albums_list)
    df.to_csv(path, index=False, encoding="utf-8-sig")
    return path


def load_artist_album_list(artist_name: str) -> list:
    path = get_artist_album_list_path(artist_name)

    if not os.path.exists(path):
        return []

    df = pd.read_csv(path)
    return df.to_dict(orient="records")


def load_artists() -> list:
    path = get_artists_csv_path()

    if not os.path.exists(path):
        return []

    df = pd.read_csv(path)
    return df.to_dict(orient="records")


def list_downloaded_albums_for_artist(artist_name: str) -> list:
    artist_name_formate = normalize_file_name(artist_name)
    artist_directory = os.path.join("db", "albums", artist_name_formate)

    if not os.path.exists(artist_directory):
        return []

    albums = []
    for file_name in os.listdir(artist_directory):
        if file_name.endswith(".csv"):
            albums.append(
                {
                    "album_name": os.path.splitext(file_name)[0],
                    "file_path": os.path.join(artist_directory, file_name),
                }
            )

    albums.sort(key=lambda album: album["album_name"].lower())
    return albums


def load_album_tracks_from_csv(file_path: str) -> list:
    with open(file_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        tracks = []

        for row in reader:
            row["track_number"] = int(row["track_number"])
            row["disc_number"] = int(row["disc_number"])
            row["duration_ms"] = int(row["duration_ms"])
            row["rate"] = int(row["rate"])
            row["superstar"] = str(row["superstar"]) == "True"
            tracks.append(row)

        return tracks


def open_csv_file(file_path: str) -> list:
    with open(file_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)

        file_name = os.path.splitext(os.path.basename(file_path))[0]
        print(f"\n{file_name}")

        print(f"{'Nr':<3} | {'TytuÅ‚ Utworu':<30} | {'Artysta':<25} | {'Czas':<5} | {'Ocena':<6} | {'Data oceny'}")
        print("-" * 95)

        for track in reader:
            special = "*" if track["superstar"] == "True" else " "

            tytul = track["title"][:27] + "..." if len(track["title"]) > 30 else track["title"]
            artysta = track["artist"][:22] + "..." if len(track["artist"]) > 25 else track["artist"]

            czas = format_ms(int(track["duration_ms"]))
            ocena = f"{track['rate']}{special}"

            print(f"{track['track_number']:<3} | {tytul:<30} | {artysta:<25} | {czas:<5} | {ocena:<6} | {track['rate_date']}")

        print("-" * 95)
