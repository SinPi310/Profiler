import os
import csv
import spotipy
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
from csv_utilities import album_csv_exists
from csv_utilities import load_artist_album_list
from csv_utilities import normalize_file_name
from csv_utilities import save_artist_album_list

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

def save_to_csv(tracks_list: list, album_name: str, artist_name: str) -> str:
    artist_name_formate = normalize_file_name(artist_name)
    album_name_formate = normalize_file_name(album_name)
    album_directory = os.path.join("db", "albums", artist_name_formate)
    os.makedirs(album_directory, exist_ok=True)
    path = os.path.join(album_directory, f"{album_name_formate}.csv")

    df = pd.DataFrame(tracks_list)
    df.to_csv(path, index=False, encoding='utf-8-sig')

    return path

def open_csv_file(file_path: str) -> list:
    with open(file_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)

        file_name = os.path.splitext(os.path.basename(file_path))[0]
        print(f"\n{file_name}")

        print(f"{'Nr':<3} | {'Tytuł Utworu':<30} | {'Artysta':<25} | {'Czas':<5} | {'Ocena':<6} | {'Data oceny'}")
        print("-" * 95)

        for track in reader:
            special = "*" if track['superstar'] == 'True' else " "

            tytul = track['title'][:27] + "..." if len(track['title']) > 30 else track['title']
            artysta = track['artist'][:22] + "..." if len(track['artist']) > 25 else track['artist']

            czas = format_ms(int(track['duration_ms']))
            ocena = f"{track['rate']}{special}"
            
            print(f"{track['track_number']:<3} | {tytul:<30} | {artysta:<25} | {czas:<5} | {ocena:<6} | {track['rate_date']}")

        print("-" * 95)

def rate_tracks(track_list: list, album_name: str) -> list:
    print("\nHi, \npleace type rate, between 1 and 10, after the track name. \nPS. You can also type [ * ] for super ultra grate tracks")
    print("")
    print(album_name.upper())

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
                print("Invalid user input!!!")

    return track_list

def should_continue_with_existing_album(album_name: str, artist_name: str) -> bool:
    if not album_csv_exists(album_name, artist_name):
        return True

    print(f"Album '{album_name}' by '{artist_name}' is already downloaded and rated.")
    user_choice = input("Do you want to rate it again? (y/n): ").strip().lower()
    return user_choice == "y"

def add_album_by_link(sp: spotipy.Spotify) -> None:
    link = input("Pass your spotify album link: ").strip()

    try:
        album_data = sp.album(link)
        album_name = album_data['name']
        artist_name = album_data['artists'][0]['name']

        if not should_continue_with_existing_album(album_name, artist_name):
            print("Skipping album.")
            return

        row_album_data = album_download(sp, link)
        rated_album = rate_tracks(row_album_data, album_name)
        path = save_to_csv(rated_album, album_name, artist_name)
        ensure_artist_album_list(sp, artist_name)

        print(f"Thanks for rating! Your data has been saved to {path}")

    except Exception as e:
        print(f"An error occurred: {e}")

def ensure_artist_album_list(sp: spotipy.Spotify, artist_name: str) -> list:
    albums_list = load_artist_album_list(artist_name)

    if albums_list:
        return albums_list

    return get_artist_albums(sp, artist_name)

def get_artist_albums(sp: spotipy.Spotify, artist_name: str) -> list:
    albums_list = load_artist_album_list(artist_name)

    if albums_list:
        return albums_list
    else:
        try:
            search_result = sp.search(q=f"artist:{artist_name}", type="artist", limit=1)
            artists = search_result["artists"]["items"]

            if not artists:
                return []

            artist = artists[0]
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
                        "album_name": album_name,
                        "album_url": album["external_urls"]["spotify"],
                        "total_tracks": album["total_tracks"],
                        "release_date": album["release_date"],
                    }
                )

            save_artist_album_list(albums_list, artist["name"])

        except Exception as e:
            print(f"An error occurred: {e}")
            return []

    return albums_list

def download_and_rate_selected_album(sp: spotipy.Spotify, album_data: dict) -> str | None:
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

def menu(sp):
    print("\n+---------------------------------------+")
    print("|         Spotify Album rater           |")
    print("+---------------------------------------+")
    print("| 1. Add album                          |")
    print("| 2. Analyze ratings                    |")
    print("| 3. Open CSV file                      |")
    print("| 4. Exit                               |")
    print("+---------------------------------------+")

    choice = input("Enter your choice (1-4): ")

    # ================ Choice 1 =====================
    if choice == '1':
        add_album_menu(sp)


    # ================ Choice 2 =====================
    # Doczytać z tym sortowanie jak to wygląda
    elif choice == '2':
        print("\nWhich one to analyze?")

        files = [f for f in os.listdir("DB") if f.endswith('.csv')]
        
        albums_with_dates = []

        for file in files:
            file_path = os.path.join("DB", file)
            try:
                df_temp = pd.read_csv(file_path)
                
                if 'rate_date' in df_temp.columns and not df_temp['rate_date'].isnull().all():
                    rate_date = str(df_temp['rate_date'].dropna().iloc[0])
                else:
                    rate_date = "Brak daty"
            except Exception:
                rate_date = "Brak daty"
                
            albums_with_dates.append({"file": file, "date": rate_date})

        albums_with_dates.sort(key=lambda x: x["date"] if x["date"] != "Brak daty" else "0000-00-00", reverse=True)

        for item in albums_with_dates:
            clean_name = item['file'].replace('.csv', '')
            print(f"    [{item['date']}] {clean_name}")

        filed_name = input("\nEnter the name of the CSV file to analyze (without .csv): ").strip()
        
        filed_path = os.path.join("DB", f"{filed_name}.csv")
        
        if os.path.exists(filed_path):
            analyze_ratings(filed_path)
        else:
            print(f"❌ File not found: {filed_path}")


    # ================ Choice 3 =====================
    elif choice == '3':
        print("\nAvailable CSV files in the 'DB' directory:")

        files = [f for f in os.listdir("DB") if f.endswith('.csv')]

        for file in files:
            print(f"    {file}")

        filed_name = input("\nEnter the name of the CSV file to open (without .csv): ").strip()
        filed_path = os.path.join("DB", f"{filed_name}.csv")

        if os.path.exists(filed_path):
            open_csv_file(filed_path)
        else:
            print("File not found.")


    # ================ Choice 4 =====================
    elif choice == '4':
        print("Exiting the program...")
        return
    
    else:
        print("Invalid choice. Please try again.")

def analyze_ratings(file_path: str) -> None:
    df = pd.read_csv(file_path)

    if df.empty:
        print("No data found.")
        return
    
    df['duration_s'] = df['duration_ms'].apply(format_ms)

    average_grade = df['rate'].mean()
    album_name = os.path.splitext(os.path.basename(file_path))[0]

    fig, ax = plt.subplots(nrows=2, ncols=2, figsize=(14, 9))
    fig.suptitle(f"{album_name.upper()} ({average_grade:.2f}/10)", fontsize=18, fontweight='bold')

    # ================ Wykres 1 =====================
    # ================ ax[0, 0] =====================
    skrocone_tytuly = [tytul[:20] + '...' if len(tytul) > 20 else tytul for tytul in df['title']]

    superstar_colour_all = ['gold' if str(star) == 'True' else 'mediumpurple' for star in df['superstar']]

    ax[0, 0].set_title("All tracks")
    ax[0, 0].bar(skrocone_tytuly, df['rate'], color=superstar_colour_all, edgecolor='black')
    ax[0, 0].set_ylabel("Rate")
    ax[0, 0].set_ylim(0, 11)
    ax[0, 0].tick_params(axis='x', rotation=90, labelsize=9)
    # ===============================================


    # ================ Wykres 2 =====================
    # ================ ax[0, 1] =====================
    top5 = df.sort_values(by='rate', ascending=False).head(5).sort_values(by='rate', ascending=True)

    superstar_colour_top5 = ['gold' if str(star) == 'True' else 'mediumpurple' for star in top5['superstar']]

    ax[0, 1].barh(y=top5['title'], width=top5['rate'], color=superstar_colour_top5, edgecolor='black')
    ax[0, 1].set_title("Top 5")
    ax[0, 1].set_xlim(0, 11)
    
    for i, (ocena, star) in enumerate(zip(top5['rate'], top5['superstar'])):
        special = "*" if str(star) == 'True' else ""
        ax[0, 1].text(ocena + 0.2, i, f"{ocena}{special}", va='center', fontweight='bold')
    # ===============================================


    # ================ Wykres 3 =====================
    # ================ ax[1, 0] =====================
    ax[1, 0].axis('off')

    table_data = []
    for _, row in df.iterrows():
        table_data.append([row['title'], str(row['artist']), format_ms(row['duration_ms'])])

    szerokosci_kolumn = [0.45, 0.40, 0.15]

    tabela = ax[1, 0].table(cellText=table_data, colWidths=szerokosci_kolumn, loc='center', cellLoc='left')

    tabela.auto_set_font_size(False)
    font_size = 9 if len(df) <= 15 else 7
    tabela.set_fontsize(font_size)
    tabela.scale(1, 1.4)
    # ===============================================


    # ================ Wykres 4 =====================
    # ================ ax[1, 1] =====================
    superstar_counts = df['superstar'].astype(str).value_counts()

    superstar_colour_pie = ['gold' if val == 'True' else 'mediumpurple' for val in superstar_counts.index]
    etykiety = ["Superstars" if val == 'True' else "Casual" for val in superstar_counts.index]
    
    ax[1, 1].pie(superstar_counts.values, labels=etykiety, autopct='%1.1f%%', startangle=90, colors=superstar_colour_pie, radius=1.2, textprops={'fontsize': 11})
    ax[1, 1].set_title("Amount of superstar tracks in the album")
    # ===============================================

    plt.tight_layout()
    plt.show()

def format_ms(ms: int) -> str:
    minutes = int((ms / (1000 * 60)) % 60)
    seconds = int((ms / 1000) % 60)
    return f"{minutes:02d}:{seconds:02d}"
