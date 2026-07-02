import csv
import os

import pandas as pd

from analysis import format_ms


def save_to_csv(tracks_list: list, album_name: str) -> str:
    os.makedirs("DB", exist_ok=True)
    album_name_formate = "".join([c for c in album_name if c.isalnum() or c in " _-"]).rstrip()
    path = os.path.join("DB", f"{album_name_formate}.csv")

    df = pd.DataFrame(tracks_list)
    df.to_csv(path, index=False, encoding="utf-8-sig")

    return path


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
