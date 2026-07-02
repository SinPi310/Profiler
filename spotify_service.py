import spotipy

from csv_utilities import load_artist_album_list
from csv_utilities import save_artist_if_missing
from csv_utilities import save_artist_album_list
from csv_utilities import save_to_csv
from db_service import should_continue_with_existing_album
from rating import rate_tracks


def album_download(sp: spotipy.Spotify, album_url: str) -> list:
    print("+---------------------------------------+")
    print("|       Downloading tracks...           |")

    result = sp.album_tracks(album_url)
    tracks = result["items"]
    tracks_list = []

    while result["next"]:
        result = sp.next(result)
        tracks.extend(result["items"])

    for track in tracks:
        track_info = {
            "id": track["id"],
            "title": track["name"],
            "artist": ", ".join([artist["name"] for artist in track["artists"]]),
            "disc_number": track["disc_number"],
            "track_number": track["track_number"],
            "duration_ms": track["duration_ms"],
            "rate": 0,
            "superstar": False,
            "rate_date": "",
        }
        tracks_list.append(track_info)

    print(f"|         Downloaded {len(tracks_list)} tracks!         |")
    print("+---------------------------------------+")
    return tracks_list


def ensure_artist_album_list(sp: spotipy.Spotify, artist_name: str) -> list:
    albums_list = load_artist_album_list(artist_name)

    if albums_list:
        return albums_list

    return get_artist_albums(sp, artist_name)


def add_album_by_link(sp: spotipy.Spotify) -> None:
    link = input("Pass your spotify album link: ").strip()

    try:
        album_data = sp.album(link)
        album_name = album_data["name"]
        artist_name = album_data["artists"][0]["name"]
        artist_id = album_data["artists"][0].get("id", "")

        if not should_continue_with_existing_album(album_name, artist_name):
            print("Skipping album.")
            return

        row_album_data = album_download(sp, link)
        rated_album = rate_tracks(row_album_data, album_name)
        path = save_to_csv(rated_album, album_name, artist_name)
        save_artist_if_missing(artist_name, artist_id)
        ensure_artist_album_list(sp, artist_name)

        print(f"Thanks for rating! Your data has been saved to {path}")

    except Exception as e:
        print(f"An error occurred: {e}")


def get_artist_albums(sp: spotipy.Spotify, artist_name: str) -> list:
    albums_list = load_artist_album_list(artist_name)

    if albums_list:
        cached_artist_id = ""
        if "artist_id" in albums_list[0]:
            cached_artist_id = str(albums_list[0]["artist_id"])

        save_artist_if_missing(artist_name, cached_artist_id)
        return albums_list

    try:
        search_result = sp.search(q=f"artist:{artist_name}", type="artist", limit=1)
        artists = search_result["artists"]["items"]

        if not artists:
            return []

        artist = artists[0]
        save_artist_if_missing(artist["name"], artist["id"])

        results = sp._get(
            f"artists/{artist['id']}/albums",
            include_groups="album",
        )
        albums = results["items"]

        while results["next"]:
            results = sp.next(results)
            albums.extend(results["items"])

        seen_album_names = set()
        albums_list = []

        for album in albums:
            album_name = album["name"]

            if album_name in seen_album_names:
                continue

            seen_album_names.add(album_name)
            albums_list.append(
                {
                    "artist_name": artist["name"],
                    "artist_id": artist["id"],
                    "album_name": album_name,
                    "album_url": album["external_urls"]["spotify"],
                    "total_tracks": album["total_tracks"],
                    "release_date": album["release_date"],
                }
            )

        save_artist_album_list(albums_list, artist["name"])
        return albums_list

    except Exception as e:
        print(f"An error occurred: {e}")
        return []
