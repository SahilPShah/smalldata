import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import json
import spotipy.util as util
from smallData import spotutil as util2
import os;



def main():
    name = 'Chance the Rapper'
    client_credentials_manager = SpotifyClientCredentials('327541285c7343afbf4822dc9d30ef7f', client_secret='713dbe89b2ea4bd382fb0a7b366a63bb')
    username='sahil5'
    scope = 'user-library-read'
    token = util.prompt_for_user_token(username, scope, client_id='327541285c7343afbf4822dc9d30ef7f',
                               client_secret='713dbe89b2ea4bd382fb0a7b366a63bb', redirect_uri='http://smalldata411.web.illinois.edu/redirect')
    if token:
        sp = spotipy.Spotify(auth=token, client_credentials_manager=client_credentials_manager)
        results = sp.current_user_saved_tracks(limit=50) #max limit is fifty songs...use paging to scroll through results
        tracks = results['items']
        while results['next']:
            results = sp.next(results)
            tracks.extend(results['items']) #tracks is a list

        print (len(tracks))
        for track in tracks:
            song = track['track']
            print (song['name'] + ' - ' + song['artists'][0]['name'])

if __name__ == "__main__":  main()


