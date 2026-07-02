from csv_utilities import album_csv_exists
from csv_utilities import load_album_tracks_from_csv
from csv_utilities import save_to_csv
from rating import rate_tracks


def should_continue_with_existing_album(album_name: str, artist_name: str) -> bool:
    if not album_csv_exists(album_name, artist_name):
        return True

    print(f"Album '{album_name}' by '{artist_name}' is already downloaded and rated.")
    user_choice = input("Do you want to rate it again? (y/n): ").strip().lower()
    return user_choice == "y"


def download_and_rate_selected_album(sp, album_data: dict, album_download) -> str | None:
    album_name = album_data["album_name"]
    album_url = album_data["album_url"]
    artist_name = album_data["artist_name"]

    try:
        if not should_continue_with_existing_album(album_name, artist_name):
            print("Skipping album.")
            return None

        row_album_data = album_download(sp, album_url)
        rated_album = rate_tracks(row_album_data, album_name)
        path = save_to_csv(rated_album, album_name, artist_name)
        return path
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def rerate_album_from_file(file_path: str, artist_name: str, album_name: str) -> str | None:
    try:
        track_list = load_album_tracks_from_csv(file_path)
        rated_album = rate_tracks(track_list, album_name)
        path = save_to_csv(rated_album, album_name, artist_name)
        return path
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
