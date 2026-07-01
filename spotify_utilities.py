import os
import csv
import spotipy
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

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

def save_to_csv(tracks_list: list, album_name: str) -> str:
    os.makedirs("DB", exist_ok=True)
    album_name_formate = "".join([c for c in album_name if c.isalnum() or c in " _-"]).rstrip()
    path = os.path.join("DB", f"{album_name_formate}.csv")

    df = pd.DataFrame(tracks_list)
    df.to_csv(path, index=False, encoding='utf-8-sig')

    return path

def open_csv_file(file_path: str) -> list:
    with open(file_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)

        file_name = os.path.splitext(os.path.basename(file_path))[0]
        print(f"\n{file_name}")

        for track in reader:
            special = "*" if track['superstar'] else ""
            print(f"{track['track_number']}. {track['title']} [{track['artist']}]   {track['rate']}{special}")

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

def menu(sp):
    print("\n+---------------------------------------+")
    print("|         Spotify Album rater           |")
    print("+---------------------------------------+")
    print("| 1. Download album and rate            |")
    print("| 2. Open CSV file                      |")
    print("| 3. Analyze ratings                    |")
    print("| 4. Exit                               |")
    print("+---------------------------------------+")

    choice = input("Enter your choice (1-4): ")

    if choice == '1':
        link = input("Pass your spotify album link: ").strip()

        try:
            album_data = sp.album(link)
            album_name = album_data['name']

            row_album_data = album_download(sp, link)
            rated_album = rate_tracks(row_album_data, album_name)
            path = save_to_csv(rated_album, album_name)

            print(f"Thanks for rating! Your data has been saved to {path}")

        except Exception as e:
            print(f"An error occurred: {e}")

    # Opcja 2, 3 i 4 do dokończenia
    elif choice == '2':
        print("\nAvailable CSV files in the 'DB' directory:")

        files = [f for f in os.listdir("DB") if f.endswith('.csv')]

        for file in files:
            print(f" - {file}")

        filed_name = input("\nEnter the name of the CSV file to open (without .csv): ").strip()
        filed_path = os.path.join("DB", f"{filed_name}.csv")

        if os.path.exists(filed_path):
            open_csv_file(filed_path)
        else:
            print("File not found.")

    elif choice == '3':
        print("\nWith one to analyze?")

        files = [f for f in os.listdir("DB") if f.endswith('.csv')]

        for file in files:
            print(f" - {file}")

        filed_name = input("\nEnter the name of the CSV file to analyze (without .csv): ").strip()
        filed_path = os.path.join("DB", f"{filed_name}.csv")
        analyze_ratings(filed_path)

    elif choice == '4':
        print("Exiting the program.")
        return
    
    else:
        print("Invalid choice. Please try again.")

def analyze_ratings(file_path: str) -> None:
    df = pd.read_csv(file_path)

    if df.empty:
        print("No data found.")
        return
    
    df['duration_s'] = df['duration_ms'].apply(format_ms)

    album_name = os.path.splitext(os.path.basename(file_path))[0]

    fig, ax = plt.subplots(nrows=2, ncols=2, figsize=(14, 9))
    fig.suptitle(album_name.upper(), fontsize=18, fontweight='bold')

    superstar_colour = ['gold' if str(star) == 'True' else 'mediumpurple' for star in df['superstar']]

    # ================ ax[0, 1] =====================
    # Zliczamy, ile razy padła jaka ocena
    skrocone_tytuly = [tytul[:20] + '...' if len(tytul) > 20 else tytul for tytul in df['title']]

    oceny_zliczone = df['rate'].value_counts().sort_index()
    
    # Rysujemy pionowe słupki (podobnie jak w zadaniu na uczelni)
    ax[0, 0].bar(skrocone_tytuly, df['rate'], color=superstar_colour, edgecolor='black')
    ax[0, 0].set_title("Oceny poszczególnych utworów z albumu")
    ax[0, 0].set_ylabel("Twoja Ocena (1-10)")
    ax[0, 0].set_ylim(0, 11) # Dajemy trochę miejsca na górze (skala 0-11)
    ax[0, 0].tick_params(axis='x', rotation=90, labelsize=9)
    # ===============================================


    # ================ ax[0, 1] =====================
    # Sortujemy malejąco po ocenie i bierzemy 5 pierwszych (najlepszych)
    top5 = df.sort_values(by='rate', ascending=False).head(5).sort_values(by='rate', ascending=True)

    superstar_colour = ['gold' if str(star) == 'True' else 'mediumpurple' for star in df['superstar']]
    ax[0, 1].barh(y=top5['title'], width=top5['rate'], color=superstar_colour, edgecolor='black')
    ax[0, 1].set_title("Top 5")
    ax[0, 1].set_xlim(0, 11)
    
    # Podpisy z wartością na końcach słupków (znane z wykres_slupkowy!)
    for i, (ocena, star) in enumerate(zip(top5['rate'], top5['superstar'])):
        special = "*" if str(star) == 'True' else ""
        ax[0, 1].text(ocena + 0.2, i, f"{ocena}{special}", va='center', fontweight='bold')
    # ===============================================


    # ================ ax[1, 0] =====================
    # Wykres punktowy sprawdzający, czy wolisz długie czy krótkie utwory
    ax[1, 0].axis('off') # Wyłączamy osie (x i y), żeby narysować tabelę
    ax[1, 0].set_title("Lista utworów", pad=10, fontweight='bold')
    
    # Funkcja pomocnicza do formatowania czasu z ms na minuty:sekundy
    def format_duration(ms):
        minutes = int((ms / (1000 * 60)) % 60)
        seconds = int((ms / 1000) % 60)
        return f"{minutes:02d}:{seconds:02d}"

    # Przygotowanie danych do tabeli (skracamy długie teksty)
    table_data = []
    for _, row in df.iterrows():
        tytul = row['title'][:22] + '...' if len(row['title']) > 22 else row['title']
        artysta = str(row['artist'])[:20] + '...' if len(str(row['artist'])) > 20 else str(row['artist'])
        czas = format_duration(row['duration_ms'])
        table_data.append([row['track_number'], tytul, artysta, czas])
    
    # Rysowanie tabeli
    tabela = ax[1, 0].table(cellText=table_data, loc='right', cellLoc='right')
    
    # Stylizacja tabeli (odpowiednia wielkość czcionki, by zmieściły się dłuższe albumy)
    tabela.auto_set_font_size(False)
    
    # Dynamiczne dopasowanie czcionki: mniejsza, jeśli piosenek jest dużo (np. powyżej 12)
    font_size = 9 if len(df) <= 12 else 7 
    tabela.set_fontsize(font_size)
    tabela.scale(1, 1.3) # Lekko rozciągamy wiersze, by nie były zbytnio ściśnięte
    # ===============================================


    # ================ ax[1, 1] =====================
    superstar_counts = df['superstar'].astype(str).value_counts()

    superstar_colour = ['gold' if str(star) == 'True' else 'mediumpurple' for star in df['superstar']]
    etykiety = ["Superstar (Hity)" if val == 'True' else "Standardowe" for val in superstar_counts.index]
    
    ax[1, 1].pie(superstar_counts.values, labels=etykiety, autopct='%1.1f%%', startangle=90, colors=superstar_colour)
    ax[1, 1].set_title("Ile procent albumu to super hity?")
    # ===============================================

    plt.tight_layout()
    plt.show()

def format_ms(ms: int) -> str:
    minutes = int((ms / (1000 * 60)) % 60)
    seconds = int((ms / 1000) % 60)
    return f"{minutes:02d}:{seconds:02d}"
