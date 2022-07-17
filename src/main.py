# Created: Feb 09 2022
# Spotify Playlist Exporter

import json
import os
import argparse
import datetime
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyOauthError
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyStateError
from dotenv import load_dotenv

URI = "http://127.0.0.1:9090"
PLAYLIST_READ_SCOPE = "playlist-read-private"
LIBRARY_READ_SCOPE = "user-library-read"
CLIENT_ID = ""
CLIENT_KEY = ""
USERNAME = ""

# TO DO:
# Get all liked albums


def configure():
    load_dotenv()

    global CLIENT_ID, CLIENT_KEY, USERNAME
    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_KEY = os.getenv("CLIENT_KEY")
    USERNAME = os.getenv("USERNAME")


def getOAuth(scope):
    auth = None
    try:
        auth = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                                         client_secret=CLIENT_KEY, redirect_uri=URI, scope=LIBRARY_READ_SCOPE))
    except SpotifyOauthError:
        print("ERROR: Unable to authenticate user")
        return(-1)

    return auth


def getClientAuth():
    auth = None
    try:
        auth = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
            client_id=CLIENT_ID, client_secret=CLIENT_KEY))

    except SpotifyStateError:
        print("ERROR: Unable to create Client Auth")
        return(-1)

    return auth


def getPlaylistName(sp, playlistId):
    res = sp.playlist(playlistId)
    return res["name"]


def getArtists(data):
    artistList = data["track"]["artists"]
    artists = []
    for a in artistList:
        genres = getArtistGenre(a["id"])
        artists.append(
            {"name": a["name"],
             "genres": genres})

    return artists


def getArtistGenre(artistId):
    sp = getClientAuth()
    artist = sp.artist(artistId)

    return artist["genres"]


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

    playlistTracks = processSavedTracks(trackData)
    return playlistTracks


def getPlaylists(sp):
    res = sp.current_user_playlists()
    data = {}

    for playlist in res["items"]:
        id = playlist["id"]
        name = getPlaylistName(sp, id)
        print("\tProcessing playlist %s" % (name))
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


def createFile(filename, data):
    curDatetime = datetime.datetime.now().strftime("%m%d%Y-%H%M%S")
    fullFilename = filename + "-" + curDatetime
    # print(curDatetime)

    with open("%s.json" % (fullFilename), "w") as fp:
        try:
            json.dump(data, fp)
        except:
            print("Unable to export playlists")
            return(-1)

        curDir = os.getcwd()
        print("%s created at %s" % (fullFilename, curDir))
        return(0)


def main():
    configure()

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--playlists",
                        help="Export playlists to provided filename")
    parser.add_argument(
        "-t", "--tracks", help="Export saved tracks to provided filename")
    args = parser.parse_args()
    # print(args)

    if (not args.tracks) and (not args.playlists):
        print("You must specify at least one option.\nCheck --help for more information.")
        return(-1)

    if args.tracks and not args.playlists:
        scope = "user-library-read"
        sp = getOAuth(scope)

        print("Exporting Saved Tracks...")
        data = getSavedTracks(sp)
        createFile(args.tracks, data)

    elif args.playlists and not args.tracks:
        scope = "playlist-read-private"
        sp = getOAuth(scope)

        print("Exporting Saved Playlists...")
        data = getPlaylists(sp)
        createFile(args.playlists, data)

    elif args.tracks and args.playlists:
        scope = "user-library-read playlist-read-private"
        sp = getOAuth(scope)

        print("Exporting Saved Playlists...")
        playlistData = getPlaylists(sp)
        createFile(args.playlists, playlistData)

        print("Exporting Saved Tracks...")
        trackData = getSavedTracks(sp)
        createFile(args.tracks, trackData)


if __name__ == "__main__":
    main()
