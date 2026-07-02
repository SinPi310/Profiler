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

def menu(sp: spotipy.Spotify) -> None:
    while True:
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

        action_completed = False

        if choice == '1':
            action_completed = add_album_menu(sp)
        elif choice == '2':
            action_completed = rerate_album_menu()
        elif choice == '3':
            action_completed = analyze_ratings_menu()
        elif choice == '4':
            action_completed = open_csv_menu()
        elif choice == '5':
            print("Exiting the program...")
            return
        else:
            print("Invalid choice. Please try again.")
            continue

        if not action_completed:
            continue

        back_to_menu = input("\nBack to main menu? (y/n): ").strip().lower()
        if back_to_menu != "y":
            print("Exiting the program...")
            return

def choose_artist() -> str | None:
    artists = load_artists()

    if not artists:
        print("No artists found.")
        return None

    while True:
        print("\nChoose artist:")
        for index, artist in enumerate(artists, start=1):
            print(f"{index}. {artist['artist_name']}")

        selected_artist = input("\nChoose artist number (or b to go back): ").strip().lower()

        if selected_artist == "b":
            return None

        try:
            artist_index = int(selected_artist) - 1
        except ValueError:
            print("Invalid artist number.")
            continue

        if artist_index < 0 or artist_index >= len(artists):
            print("Artist number out of range.")
            continue

        return artists[artist_index]["artist_name"]


def choose_downloaded_album(artist_name: str, action_label: str) -> dict | None:
    albums = list_downloaded_albums_for_artist(artist_name)

    if not albums:
        print("No downloaded albums found for this artist.")
        return None

    while True:
        print(f"\nChoose album to {action_label}:")
        for index, album in enumerate(albums, start=1):
            print(f"{index}. {album['album_name']}")

        selected_album = input("\nChoose album number (or b to go back): ").strip().lower()

        if selected_album == "b":
            return None

        try:
            album_index = int(selected_album) - 1
        except ValueError:
            print("Invalid album number.")
            continue

        if album_index < 0 or album_index >= len(albums):
            print("Album number out of range.")
            continue

        return albums[album_index]


def add_album_menu(sp: spotipy.Spotify) -> bool:
    while True:
        print("\nAdd album:")
        print("1. Add by album link")
        print("2. Search artist and albums")

        add_choice = input("Enter your choice (1-2, or b to go back): ").strip().lower()

        if add_choice == "b":
            return False

        if add_choice == '1':
            add_album_by_link(sp)
            return True

        if add_choice != '2':
            print("Invalid choice. Please try again.")
            continue

        while True:
            artist_name = input("Pass artist name (or b to go back): ").strip()

            if artist_name.lower() == "b":
                break

            if not artist_name:
                print("Artist name cannot be empty.")
                continue

            albums_list = get_artist_albums(sp, artist_name)

            if not albums_list:
                print("No albums found.")
                continue

            while True:
                print("\nAlbums:")
                for index, album in enumerate(albums_list, start=1):
                    print(f"{index}. {album['album_name']} [{album['release_date']}] ({album['total_tracks']} tracks)")

                selected_album = input("\nChoose album number (or b to go back): ").strip().lower()

                if selected_album == "b":
                    break

                try:
                    selected_index = int(selected_album) - 1
                except ValueError:
                    print("Invalid album number.")
                    continue

                if selected_index < 0 or selected_index >= len(albums_list):
                    print("Album number out of range.")
                    continue

                selected_album_data = albums_list[selected_index]
                path = download_and_rate_selected_album(sp, selected_album_data, album_download)

                if path:
                    print(f"Thanks for rating! Your data has been saved to {path}")

                return True


def rerate_album_menu() -> bool:
    while True:
        artist_name = choose_artist()

        if not artist_name:
            return False

        selected_album_data = choose_downloaded_album(artist_name, "rerate")

        if not selected_album_data:
            continue

        path = rerate_album_from_file(
            selected_album_data["file_path"],
            artist_name,
            selected_album_data["album_name"],
        )

        if path:
            print(f"Album rerated and saved to {path}")

        return True


def analyze_ratings_menu() -> bool:
    while True:
        artist_name = choose_artist()

        if not artist_name:
            return False

        selected_album_data = choose_downloaded_album(artist_name, "analyze")

        if not selected_album_data:
            continue

        analyze_ratings(selected_album_data["file_path"])
        return True


def open_csv_menu() -> bool:
    while True:
        artist_name = choose_artist()

        if not artist_name:
            return False

        selected_album_data = choose_downloaded_album(artist_name, "open")

        if not selected_album_data:
            continue

        open_csv_file(selected_album_data["file_path"])
        return True
