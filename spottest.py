import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import json
import spotipy.util as util
import os;


username = "sahil5"
scope = 'user-library-read'
client_credentials_manager = SpotifyClientCredentials('327541285c7343afbf4822dc9d30ef7f',
                                                      client_secret='713dbe89b2ea4bd382fb0a7b366a63bb')
spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
spotify.trace = False

<<<<<<< HEAD
def spotsearch_track(trackname):
    results = spotify.search(q='track:' + trackname, type='track')
    items = results['tracks']['items']
    #print (results['tracks']['items'])
    for element in items:
        print (element['name'] + " - " + element['artists'][0]['name'])
    return results

def spotsearch_artist(artistname):
    results = spotify.search(q='artist:' + artistname, type='artist')
    items = results['artists']['items']
    print (results['artists']['items'])
    for artists in items:
        print (artists)
    return results

def get_recommendations():
    songs = []
    songIds = []
    songs.append(('No Problem', 'Chance the Rapper'))
    songs.append(('Juke Jam', 'Chance the Rapper'))
    songs.append(('Same Drugs', 'Chance the Rapper'))
    songs.append(('I Might Need Security', 'Chance the Rapper'))
    songs.append(('All Night', 'Chance the Rapper'))

    for song in songs:
        name = str(song[0])
        results = spotify.search(q='track:' + name, type='track')
        results = results['tracks']['items']
        for hit in results:
            if str(hit['artists'][0]['name']) == str(song[1]):
                songIds.append(hit["id"])


    songId = songIds[0]
    songIds = list(songIds)
    recs = spotify.recommendations(seed_tracks=songIds, limit = 5)
    recs=recs['tracks']
    for track in recs:
        print (track['name'] + " - " + track['artists'][0]['name'] + " - " + track['album']['name'])

def get_audio_features(songname):
    results = spotify.search(q='track:' + songname, type='track')
    songs = results['tracks']['items']
    songId = songs[0]['id']
    print (songs[0]['name'])
    print (songs[0]['artists'][0]['name'])
    features = spotify.audio_features([songId])
    features = features[0]
    print (features)
    for e in features:
        print (e)



def main():
    # spotsearch_artist("Chance the Rapper")
    # spotsearch_track("Champions Kanye West")
    # get_recommendations()
    get_audio_features("Trip Ella Mai")
if __name__ == "__main__":  main()


