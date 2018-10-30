import spotipy
import requests
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util



class SpotScraper:
    def __init__(self):
        self.client_credentials_manager = SpotifyClientCredentials('327541285c7343afbf4822dc9d30ef7f',client_secret='713dbe89b2ea4bd382fb0a7b366a63bb')
        self.sp = spotipy.Spotify(client_credentials_manager=self.client_credentials_manager)

    def artist(self, artist):
        results = self.sp.search(q='artist:' + artist, type='artist')
        print (results)

    def user_saved_tracks(self,username):
        scope = 'user-library-read'
        token = util.prompt_for_user_token(username, scope, client_id='327541285c7343afbf4822dc9d30ef7f',
                                           client_secret='713dbe89b2ea4bd382fb0a7b366a63bb',
                                           redirect_uri='http://smalldata411.web.illinois.edu')
        if token:
            sp = spotipy.Spotify(auth=token)
            results = sp.current_user_saved_tracks(limit=50)  # max limit is fifty songs...use paging to scroll through results
            tracks = results['items']
            while results['next']:
                results = sp.next(results)
                tracks.extend(results['items'])  # tracks is a list

            return (tracks)  # see spot test for example on how to get specific track information

    #similar functions for other data retrievals need to be written (See API reference for exact functionalities)
