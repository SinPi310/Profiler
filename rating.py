from datetime import datetime


def rate_tracks(track_list: list, album_name: str) -> list:
    print("\nHi, \npleace type rate, between 1 and 10, after the track name. \nPS. You can also type [ * ] for super ultra grate tracks")
    print("")
    print(album_name.upper())

    for track in track_list:
        while True:
            user_rate = input(f" {track['track_number']}. {track['title']} [{track['artist']}] -> rate: ").strip()

            is_superstar = "*" in user_rate
            user_rate_number = user_rate.replace("*", "")

            try:
                user_rate_int = int(user_rate_number)

                if 1 <= user_rate_int <= 10:
                    track["rate"] = user_rate_int
                    track["superstar"] = is_superstar
                    track["rate_date"] = datetime.now().strftime("%Y-%m-%d")
                    break

                print("Rate must be between 1 and 10!!!")

            except ValueError:
                print("Invalid user input!!!")

    return track_list
