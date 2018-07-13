import requests
import os
import shutil
import zipfile
import json
import html
import io
import string

api = "https://beatsaver.com/api/songs/new/{}"
offset = 0

download = "https://beatsaver.com/download/{}"
downloaded_songs = []
this_session = 0
processing = True

if os.path.isfile("songs.json"):
    with open("songs.json", "r") as handle:
        downloaded_songs = json.loads(handle.read())

def escape(s): # Function for ensuring that song names are proper foldernames for windows
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    filename = ''.join(c for c in s if c in valid_chars)
    filename = filename.replace(' ','') # Remove spaces to avoid issues
    return filename

def extractZip(zip_file, song_name): # Extract zip files into folder with song name ignoring the first directory within the zip
    for zip_info in zip_file.infolist(): # for each file in the zip
        if not zip_info.filename.endswith('/') and zip_info.filename.count('/') < 2: # if its not the first directory or files in sub directories
            data = zip_file.read(zip_info.filename) # read that file
            if not os.path.exists(os.path.dirname(song_name+os.path.basename(zip_info.filename))): 
                os.makedirs(os.path.dirname(song_name+os.path.basename(zip_info.filename))) # create any directories that are needed if they dont exist
            try:
                with io.FileIO(song_name+os.path.basename(zip_info.filename), "w") as file:
                    file.write(data) # write the file to disk
            except OSError as exc:
                if True:
                    print(os.path.basename(zip_info.filename), 'FAIL')


while processing:
    response = requests.get(api.format(offset)).json()
    offset += len(response)
    if len(response) == 0:
        break
    for song in response['songs']:
        if song['id'] in downloaded_songs:
            # We found a song we already downloaded
            # Assume we've done them all
            processing = False
            break
        print("Downloading {}".format(html.unescape(song['name'])))
        this_session += 1
        response = requests.get(download.format(song['key']))
        try:
            with zipfile.ZipFile(io.BytesIO(response.content)) as song_zip:
                extractZip(song_zip, "CustomSongs/{}/".format(escape(html.unescape(song['name'])))) 
                # Write out all the files for the zip to a folder named after the songname with html escaped characters and escaping
        except:
            print("Failed to download {}. An Error occoured".format(html.unescape(song['name'])))

        # Add to downloaded
        downloaded_songs.append(song['id'])


with open("songs.json", "w") as handle:
    handle.write(json.dumps(downloaded_songs))
print("Downloaded {} song{} this session".format(this_session, 's' if this_session != 0 else ''))
print("Downloaded {} song{} in total".format(len(downloaded_songs), 's' if len(downloaded_songs) != 0 else ''))
