# Profiler

CLI app for downloading Spotify albums, rating tracks, and saving ratings to CSV files.

## Installation

```bash
python -m pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root:

```env
SPOTIPY_CLIENT_ID=your_client_id
SPOTIPY_CLIENT_SECRET=your_client_secret
```

Create your Spotify app at:

`https://developer.spotify.com/dashboard`

## Run

```bash
python .\main.py
```

## Menu

Main menu:

1. Add album
2. Rerate album
3. Analyze ratings
4. Open CSV file
5. Exit

Add album submenu:

1. Add by album link
2. Search artist and albums

## Navigation

- Enter `b` to go back one level in submenus.
- After completing an action, the app asks: `Back to main menu? (y/n)`.

## Data Structure

```text
db/
    artists.csv
    artists_albums/
        UMEK_album_list.csv
        Nujabes_album_list.csv
    albums/
        UMEK/
            Out Of Play.csv
            Toolroom Presents UMEK.csv
        Nujabes/
            Modal Soul.csv
```

## What Gets Saved

- `db/artists.csv`
  Stores known artists.

- `db/artists_albums/<artist>_album_list.csv`
  Stores cached album lists for artists, so Spotify does not need to be queried every time.

- `db/albums/<artist>/<album>.csv`
  Stores rated tracks for each downloaded album.

## Features

- Download album by Spotify link
- Search artist and choose an album from a numbered list
- Cache artist album lists locally
- Rerate already downloaded albums
- Analyze saved ratings with charts
- Open saved album CSV files from the app

## Dependencies

- `spotipy`
- `python-dotenv`
- `pandas`
- `matplotlib`

# Uwierzytelniania i testowania połączenia z API

``` py
    client_id = os.getenv("SPOTIPY_CLIENT_ID")
    client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")

    if not client_id or not client_secret or client_id == 'TWOJ_CLIENT_ID':
```

# TEST API

## TEST 1
``` py 
        # 2. NAZWA Artysty po Id
        artist = sp.artist('3Rq3YOF9YG9YfCWD4D56RZ')
        print(artist['name'])
```

``` bash
$ py profiler.py 
Nujabes
(.venv)

## TEST 2
``` py
        # 3. NAZWA albumu po linku
        adres_albumu = 'https://open.spotify.com/album/6b08FpNaFFTjc1dJ9DSWfn'
        album = sp.album(adres_albumu)
        print(album['name'])
```

``` bash
$ py profiler.py 
Modal Soul
(.venv)
```

