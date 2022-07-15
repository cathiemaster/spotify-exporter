# Created: Feb 09 2022
# Spotify Playlist Exporter

from concurrent.futures import process
import json
import os
import argparse
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

URI = "http://127.0.0.1:9090"
PLAYLIST_READ_SCOPE = "playlist-read-private"
LIBRARY_READ_SCOPE = "user-library-read"
CLIENT_ID = ""
CLIENT_KEY = ""
USERNAME = ""

# TO DO:
# Add artist genre data
# Get all liked albums

# Analytics:
# Top 25 Artists
# Top 3 Genres
# Genre Frequency


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


def getTrackId(data):
    return data["track"]["id"]


def getPlaylistTracks(sp, userId, playlistId):
    res = sp.user_playlist_tracks(userId, playlistId)

    trackData = res["items"]
    playlistTracks = []

    while res["next"]:
        res = sp.next(res)
        trackData.extend(res["items"])

    playlistTracks = processSavedTracks(t)
    return playlistTracks

    # for t in trackData:
    #     artists = getArtists(t)
    #     album = getAlbum(t)
    #     track = getTrack(t)

    #     datetime = t["added_at"]

    #     playlistTracks.append(
    #         {"datetime": datetime,
    #          "artists": artists,
    #          "album": album,
    #          "title": track})

    # return playlistTracks


def getPlaylists(sp):
    res = sp.current_user_playlists()
    data = {}

    for playlist in res["items"]:
        id = playlist["id"]
        name = getPlaylistName(sp, id)
        tracklist = getPlaylistTracks(sp, USERNAME, id)

        playlistInfo = {"id": id, "data": tracklist}

        data[name] = playlistInfo

    return data


def processSavedTracks(tracks):
    data = []

    for t in tracks:
        added = t["added_at"]
        id = getTrackId(t)
        artists = getArtists(t)
        album = getAlbum(t)
        name = getTrack(t)

        data.append({
            "datetime": added,
            "id": id,
            "title": name,
            "artists": artists,
            "album": album,
        })

    return data


def getSavedTracks(sp):
    data = []
    limit, offset = 50, 0

    res = sp.current_user_saved_tracks(limit=limit, offset=offset)
    data += processSavedTracks(res["items"])

    while res["next"]:
        offset += limit

        res = sp.current_user_saved_tracks(limit=limit, offset=offset)
        data += processSavedTracks(res["items"])

    return data


def createFile(filepath, username, data):
    with open("%s/spotify-%s.json" % (filepath, username), "w") as fp:
        try:
            json.dump(data, fp)
        except:
            print("Unable to export playlists")
            return(-1)

        print("spotify-%s.json created at %s" % (username, filepath))


def main():
    configure()

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--playlists",
                        help="Export playlists to provided filename")
    parser.add_argument(
        "-t", "--tracks", help="Export saved tracks to provided filename")
    args = parser.parse_args()
    print(args)

    if (not args.tracks) or (not args.playlists):
        print("You must specify at least one option.\nCheck --help for more information.")

    # sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
    #                      client_secret=CLIENT_KEY, redirect_uri=URI, scope=LIBRARY_READ_SCOPE))

    # data = getSavedTracks(sp)
    # # print(len(data))

    # # data = getPlaylists(sp)

    # with open("%s/spotify-tracks-%s.json" % (filepath, USERNAME), "w") as fp:
    #     try:
    #         json.dump(data, fp)
    #     except:
    #         print("Unable to export playlists")
    #         return(-1)

    #     print("spotify-tracks-%s.json created at %s" % (USERNAME, filepath))


if __name__ == "__main__":
    main()
