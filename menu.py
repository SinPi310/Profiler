import os

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


def choose_artist() -> str | None:
    artists = load_artists()

    if not artists:
        print("No artists found.")
        return None

    print("\nChoose artist:")
    for index, artist in enumerate(artists, start=1):
        print(f"{index}. {artist['artist_name']}")

    selected_artist = input("\nChoose artist number: ").strip()

    try:
        artist_index = int(selected_artist) - 1
    except ValueError:
        print("Invalid artist number.")
        return None

    if artist_index < 0 or artist_index >= len(artists):
        print("Artist number out of range.")
        return None

    return artists[artist_index]["artist_name"]


def choose_downloaded_album(artist_name: str, action_label: str) -> dict | None:
    albums = list_downloaded_albums_for_artist(artist_name)

    if not albums:
        print("No downloaded albums found for this artist.")
        return None

    print(f"\nChoose album to {action_label}:")
    for index, album in enumerate(albums, start=1):
        print(f"{index}. {album['album_name']}")

    selected_album = input("\nChoose album number: ").strip()

    try:
        album_index = int(selected_album) - 1
    except ValueError:
        print("Invalid album number.")
        return None

    if album_index < 0 or album_index >= len(albums):
        print("Album number out of range.")
        return None

    return albums[album_index]


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


def rerate_album_menu() -> None:
    artist_name = choose_artist()

    if not artist_name:
        return

    selected_album_data = choose_downloaded_album(artist_name, "rerate")

    if not selected_album_data:
        return

    path = rerate_album_from_file(
        selected_album_data["file_path"],
        artist_name,
        selected_album_data["album_name"],
    )

    if path:
        print(f"Album rerated and saved to {path}")


def analyze_ratings_menu() -> None:
    artist_name = choose_artist()

    if not artist_name:
        return

    selected_album_data = choose_downloaded_album(artist_name, "analyze")

    if not selected_album_data:
        return

    analyze_ratings(selected_album_data["file_path"])


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
        rerate_album_menu()

    elif choice == '3':
        analyze_ratings_menu()

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
