import os

import pandas as pd
import spotipy

from analysis import analyze_ratings
from csv_utilities import open_csv_file
from spotify_utilities import add_album_by_link
from spotify_utilities import search_artist_and_albums


def add_album_menu(sp: spotipy.Spotify) -> None:
    print("\nAdd album:")
    print("1. Add by album link")
    print("2. Search artist and albums")

    add_choice = input("Enter your choice (1-2): ").strip()

    if add_choice == '1':
        add_album_by_link(sp)
    elif add_choice == '2':
        search_artist_and_albums(sp)
    else:
        print("Invalid choice. Please try again.")


def menu(sp: spotipy.Spotify) -> None:
    print("\n+---------------------------------------+")
    print("|         Spotify Album rater           |")
    print("+---------------------------------------+")
    print("| 1. Add album                          |")
    print("| 2. Analyze ratings                    |")
    print("| 3. Open CSV file                      |")
    print("| 4. Exit                               |")
    print("+---------------------------------------+")

    choice = input("Enter your choice (1-4): ")

    if choice == '1':
        add_album_menu(sp)

    elif choice == '2':
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

    elif choice == '3':
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

    elif choice == '4':
        print("Exiting the program...")
        return

    else:
        print("Invalid choice. Please try again.")
