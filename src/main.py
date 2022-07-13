# Created: Feb 09 2022
# Spotify Playlist Exporter

import json
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

URI = "http://127.0.0.1:9090"
SCOPE = "playlist-read-private"
CLIENT_ID = ""
CLIENT_KEY = ""
USERNAME = ""


def configure():
    load_dotenv()

    global CLIENT_ID, CLIENT_KEY, USERNAME
    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_KEY = os.getenv("CLIENT_KEY")
    USERNAME = os.getenv("USERNAME")


def getPlaylistName(sp, playlistId):
    res = sp.playlist(playlistId)
    return res["name"]


def getArtists(data):
    artistList = data["track"]["artists"]
    artists = []
    for a in artistList:
        artists.append(a["name"])

    return artists


def getAlbum(data):
    return data["track"]["album"]["name"]


def getTrack(data):
    return data["track"]["name"]


def getPlaylistTracks(sp, userId, playlistId):
    res = sp.user_playlist_tracks(userId, playlistId)

    trackData = res["items"]
    playlistTracks = []

    while res["next"]:
        res = sp.next(res)
        trackData.extend(res["items"])

    for t in trackData:
        artists = getArtists(t)
        album = getAlbum(t)
        track = getTrack(t)

        datetime = t["added_at"]

        playlistTracks.append(
            {"datetime": datetime,
             "artists": artists,
             "album": album,
             "title": track})

    return playlistTracks


def main():
    configure()

    filename = str(input("Enter filename: "))
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                         client_secret=CLIENT_KEY, redirect_uri=URI, scope=SCOPE))

    results = sp.current_user_playlists()
    data = {}

    for p in results["items"]:
        id = p["id"]
        name = getPlaylistName(sp, id)
        tracklist = getPlaylistTracks(sp, USERNAME, id)

        playlistInfo = {"id": id, "data": tracklist}

        data[name] = playlistInfo

    with open("%s.json" % filename, "w") as fp:
        json.dump(data, fp)


if __name__ == "__main__":
    main()
