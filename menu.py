import os

import pandas as pd
import spotipy

from analysis import analyze_ratings
from csv_utilities import list_downloaded_albums_for_artist
from csv_utilities import load_artists
from csv_utilities import open_csv_file
from db_service import download_and_rate_selected_album
from db_service import rerate_album_from_file
from spotify_service import add_album_by_link
from spotify_service import album_download
from spotify_service import get_artist_albums


def add_album_menu(sp: spotipy.Spotify) -> None:
    print("\nAdd album:")
    print("1. Add by album link")
    print("2. Search artist and albums")

    add_choice = input("Enter your choice (1-2): ").strip()

    if add_choice == '1':
        add_album_by_link(sp)
    elif add_choice == '2':
        artist_name = input("Pass artist name: ").strip()

        if not artist_name:
            print("Artist name cannot be empty.")
            return

        albums_list = get_artist_albums(sp, artist_name)

        if not albums_list:
            print("No albums found.")
            return

        print("\nAlbums:")
        for index, album in enumerate(albums_list, start=1):
            print(f"{index}. {album['album_name']} [{album['release_date']}] ({album['total_tracks']} tracks)")

        selected_album = input("\nChoose album number: ").strip()

        try:
            selected_index = int(selected_album) - 1
        except ValueError:
            print("Invalid album number.")
            return

        if selected_index < 0 or selected_index >= len(albums_list):
            print("Album number out of range.")
            return

        selected_album_data = albums_list[selected_index]
        path = download_and_rate_selected_album(sp, selected_album_data, album_download)

        if path:
            print(f"Thanks for rating! Your data has been saved to {path}")
    else:
        print("Invalid choice. Please try again.")


def menu(sp: spotipy.Spotify) -> None:
    print("\n+---------------------------------------+")
    print("|         Spotify Album rater           |")
    print("+---------------------------------------+")
    print("| 1. Add album                          |")
    print("| 2. Rerate album                       |")
    print("| 3. Analyze ratings                    |")
    print("| 4. Open CSV file                      |")
    print("| 5. Exit                               |")
    print("+---------------------------------------+")

    choice = input("Enter your choice (1-5): ")

    if choice == '1':
        add_album_menu(sp)

    elif choice == '2':
        artists = load_artists()

        if not artists:
            print("No artists found.")
            return

        print("\nChoose artist:")
        for index, artist in enumerate(artists, start=1):
            print(f"{index}. {artist['artist_name']}")

        selected_artist = input("\nChoose artist number: ").strip()

        try:
            artist_index = int(selected_artist) - 1
        except ValueError:
            print("Invalid artist number.")
            return

        if artist_index < 0 or artist_index >= len(artists):
            print("Artist number out of range.")
            return

        artist_name = artists[artist_index]["artist_name"]
        albums = list_downloaded_albums_for_artist(artist_name)

        if not albums:
            print("No downloaded albums found for this artist.")
            return

        print("\nChoose album to rerate:")
        for index, album in enumerate(albums, start=1):
            print(f"{index}. {album['album_name']}")

        selected_album = input("\nChoose album number: ").strip()

        try:
            album_index = int(selected_album) - 1
        except ValueError:
            print("Invalid album number.")
            return

        if album_index < 0 or album_index >= len(albums):
            print("Album number out of range.")
            return

        selected_album_data = albums[album_index]
        path = rerate_album_from_file(
            selected_album_data["file_path"],
            artist_name,
            selected_album_data["album_name"],
        )

        if path:
            print(f"Album rerated and saved to {path}")

    elif choice == '3':
        print("\nWhich one to analyze?")

        files = [f for f in os.listdir("DB") if f.endswith(".csv")]
        albums_with_dates = []

        for file in files:
            file_path = os.path.join("DB", file)
            try:
                df_temp = pd.read_csv(file_path)

                if "rate_date" in df_temp.columns and not df_temp["rate_date"].isnull().all():
                    rate_date = str(df_temp["rate_date"].dropna().iloc[0])
                else:
                    rate_date = "Brak daty"
            except Exception:
                rate_date = "Brak daty"

            albums_with_dates.append({"file": file, "date": rate_date})

        albums_with_dates.sort(
            key=lambda x: x["date"] if x["date"] != "Brak daty" else "0000-00-00",
            reverse=True,
        )

        for item in albums_with_dates:
            clean_name = item["file"].replace(".csv", "")
            print(f"    [{item['date']}] {clean_name}")

        filed_name = input("\nEnter the name of the CSV file to analyze (without .csv): ").strip()
        filed_path = os.path.join("DB", f"{filed_name}.csv")

        if os.path.exists(filed_path):
            analyze_ratings(filed_path)
        else:
            print(f"âŒ File not found: {filed_path}")

    elif choice == '4':
        print("\nAvailable CSV files in the 'DB' directory:")

        files = [f for f in os.listdir("DB") if f.endswith(".csv")]

        for file in files:
            print(f"    {file}")

        filed_name = input("\nEnter the name of the CSV file to open (without .csv): ").strip()
        filed_path = os.path.join("DB", f"{filed_name}.csv")

        if os.path.exists(filed_path):
            open_csv_file(filed_path)
        else:
            print("File not found.")

    elif choice == '5':
        print("Exiting the program...")
        return

    else:
        print("Invalid choice. Please try again.")
