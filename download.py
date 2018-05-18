import requests
import os.path
import zipfile
import json
import html
import io

api = "https://beatsaver.com/api.php?mode=new&off={}"
offset_inc = 15
offset = 0

download = "https://beatsaver.com/files/{}.zip"
downloaded_songs = []
this_session = 0

if os.path.isfile("songs.json"):
    with open("songs.json", "r") as handle:
        downloaded_songs = json.loads(handle.read())


while True:
    response = requests.get(api.format(offset)).json()
    offset += offset_inc
    if len(response) == 0:
        break
    for song in response:
        if song['id'] in downloaded_songs:
            # We found a song we already downloaded
            # Assume we've done them all
            break
        print("Downloading {}".format(html.unescape(song['beatname'])))
        this_session += 1
        response = requests.get(download.format(song['id']))
        with zipfile.ZipFile(io.BytesIO(response.content)) as song_zip:
            song_zip.extractall("CustomSongs/.".format(song['beatname']))

        # Add to downloaded
        downloaded_songs.append(song['id'])


with open("songs.json", "w") as handle:
    handle.write(json.dumps(downloaded_songs))
print("Downloaded {} song{} this session".format(this_session, 's' if this_session != 0 else ''))
print("Downloaded {} song{} in total".format(len(downloaded_songs), 's' if len(downloaded_songs) != 0 else ''))