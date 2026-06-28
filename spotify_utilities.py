import spotipy

def album_download(sp: spotipy.Spotify, album_url: str) -> list:
    print("+---------------------------------------+")
    print("|      Pobieram utwory z albumu...      |")

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
            'duration_ms': track['duration_ms']
        }
        tracks_list.append(track_info)

    print(f"|          Pobrano {len(tracks_list)} utworów!          |")
    print("+---------------------------------------+")
    return tracks_list

def format_ms(ms: int) -> str:
    minutes = int((ms / (1000 * 60)) % 60)
    seconds = int((ms / 1000) % 60)
    return f"{minutes:02d}:{seconds:02d}"