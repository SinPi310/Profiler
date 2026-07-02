# Profiler
Muzyczny profiler do badania playlist na Spotify.

## Instalacja
```bash
python -m pip install -r requirements.txt
```


# Konfigutacja API
 - Stworzenie aplikacji na stronie [spotify/dashboard](https://developer.spotify.com/dashboard)  
 - Utworzenie własnego Tokena dostępu i wgranie go do...
```
PROFILER
    .env
```

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
```

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
