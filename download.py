import requests
import os.path
import os
import zipfile
import json
import html
import io

api = "https://beatsaver.com/api.php?mode=new&off={}"
offset_inc = 15
offset = 0

download = "https://beatsaver.com/files/{}.zip"
downloaded_songs = []

if os.path.isfile("songs.json"):
    with open("songs.json", "r") as handle:
        downloaded_songs = json.reads(handle.read())


while True:
    response = requests.get(api.format(offset)).json()
    offset += offset_inc
    if len(response) == 0:
        break
    for song in response:
        if song['id'] not in downloaded_songs:
            print("Downloading {}".format(html.unescape(song['beatname'])))
            response = requests.get(download.format(song['id']))
            with zipfile.ZipFile(io.BytesIO(response.content)) as song_zip:
                song_zip.extractall("Songs/.".format(song['beatname']))

            # Add to downloaded
            downloaded_songs.append(song['id'])
    
    with open("songs.json", "w") as handle:
        handle.write(json.dumps(downloaded_songs))
