# Created: Feb 09 2022
# Spotify Playlist Exporter

from datetime import date
import getpass
import json
import spotipy
from spotipy.oauth2 import SpotifyOAuth

CLIENT_ID = ""
CLIENT_KEY = ""
URI = "http://127.0.0.1:9090"
SCOPE = "playlist-read-private"
USERNAME = ""

# Fields:
# Playlist Name
# No. of tracks
# Creation date
# All tracks in the playlist


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
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                         client_secret=CLIENT_KEY, redirect_uri=URI, scope=SCOPE))

    results = sp.current_user_playlists()
    playlistIds = []
    for p in results["items"]:
        playlistIds.append(p["id"])

    playlistTracks = getPlaylistTracks(sp, USERNAME, "53AX7LCWWDdEAjrE5Fh8cR")
    # print(playlistTracks)


if __name__ == "__main__":
    main()
