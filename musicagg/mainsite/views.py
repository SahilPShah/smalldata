from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.views.generic import View
from django.db import connections
import spotipy
import spotipy.oauth2 as oauth2
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util
import requests
import os
import json
import matplotlib
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.template.loader import get_template
import logging
from random import shuffle
#from graphos.renderers import gchart, yui, flot, morris, highcharts, c3js, matplotlib_renderer
#from graphos.sources.simple import SimpleDataSource
#from graphos.sources.mongo import MongoDBDataSource
#from graphos.sources.model import ModelDataSource
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from matplotlib import pylab
from pylab import * 
import numpy as np 
import PIL, PIL.Image
from io import StringIO 

from rest_framework.views import APIView
from rest_framework.response import Response

def renderGraph(request):
    t = get_template('charts.html')
    frank = get_master_scatterplotdata(request)
    html = t.render({'pts':frank})
    return HttpResponse(html)
    
def getSpotList(request):
    c = connections['default'].cursor()
    vals = []
    if (request.user.id):
        sql_syn = "SELECT Artist,Title,Playlist FROM TopSongsMeta WHERE UserID={} AND Service = \'Spotify\'".format(request.user.id)
        c.execute(sql_syn,[])
        vals = c.fetchall()
    return vals
    
def getYoutubeList(request):
    c = connections['default'].cursor()
    vals = []
    if (request.user.id):
        sql_syn = "SELECT Artist,Title,Playlist FROM TopSongsMeta WHERE UserID={} AND Service = \'Youtube\'".format(request.user.id)
        c.execute(sql_syn,[])
        vals = c.fetchall()
    #raise Exception("d")
    return vals

#from mainsite import cairo
#import pycha.bar
#import sys
#sys.path.insert(0, '/home/')
testdata = [
       ['Year', 'Sales', 'Expenses', 'Items Sold', 'Net Profit'],
       ['2004', 1000, 400, 100, 600],
       ['2005', 1170, 460, 120, 710],
       ['2006', 660, 1120, 50, -460],
       ['2007', 1030, 540, 100, 490],
       ]

User = get_user_model()

log = logging.getLogger(__name__)

#specify developer credentials and redirect uri for spotify
# Create your views here.


def index(request):
    if(request.user.is_authenticated):
        if not exists_in_users(request.user.username):
            insert_user(request.user.id, request.user.username)
    t = get_template('frontend/index.html')
    spotlist = []
    tspotlist = getSpotList(request)
    if (len(tspotlist) == 0):
        spotlist = [('Nothing', 'is', 'here')]
    else:
        for s in tspotlist:
            spotlist.append(s)

    youtubelist = []
    tyoutubelist = getYoutubeList(request)

    if (len(tyoutubelist) == 0):
        youtubelist = [('Nothing', 'is', 'here')]
    else:
        for s in tyoutubelist:
            youtubelist.append(s)
    recommendations = get_user_recommendations(request)
    if(type(recommendations) is not list):
        recommendations = []
    if (len(recommendations) == 0):
        recommendations = [('No', 'recommendations', 'generated')]
    html = t.render({'user':request.user, 'spotlist':spotlist, 'youtubelist':youtubelist, 'recommendations':recommendations})
    return HttpResponse(html)
    
# old main page accessed at /indexold
def indexold(request):
    t = get_template('indexold.html')
    html = t.render({'user':request.user})
    if(request.user.is_authenticated):
        if not exists_in_users(request.user.username):
            insert_user(request.user.id, request.user.username, 0)
    return HttpResponse(html)

# def redirect(request):
#     return HttpResponse(str(request.build_absolute_uri()))
#
def spotlogin(request):
    ''' prompts the user to login if necessary and returns
        the user token suitable for use with the spotipy.Spotify
        constructor
        Parameters:
         - username - the Spotify username
         - scope - the desired scope of the request
         - client_id - the client id of your app
         - client_secret - the client secret of your app    
         - redirect_uri - the redirect URI of your app
         - cache_path - path to location to save tokens
    '''
    client_id = '327541285c7343afbf4822dc9d30ef7f'
    client_secret = '713dbe89b2ea4bd382fb0a7b366a63bb'
    redirect_uri = 'http://smalldata411.web.illinois.edu/redirect'
    cache_path = None
    username = 'sahil5'          #hardcoded now...change for later
    scope = 'user-library-read'
    if not client_id:
        client_id = os.getenv('SPOTIPY_CLIENT_ID')

    if not client_secret:
        client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')

    if not redirect_uri:
        redirect_uri = os.getenv('SPOTIPY_REDIRECT_URI')

    if not client_id:
        print('''
            You need to set your Spotify API credentials. You can do this by
            setting environment variables like so:
            export SPOTIPY_CLIENT_ID='your-spotify-client-id'
            export SPOTIPY_CLIENT_SECRET='your-spotify-client-secret'
            export SPOTIPY_REDIRECT_URI='your-app-redirect-url'
            Get your credentials at
                https://developer.spotify.com/my-applications
        ''')
        raise spotipy.SpotifyException(550, -1, 'no credentials set')

    cache_path = cache_path or ".cache-" + username
    sp_oauth = oauth2.SpotifyOAuth(client_id, client_secret, redirect_uri,
        scope=scope, cache_path=cache_path)

    # try to get a valid token for this user, from the cache,
    # if not in the cache, the create a new (this will send
    # the user to a web page where they can authorize this app)

    token_info = sp_oauth.get_cached_token()

    if not token_info:
        print('''
            User authentication requires interaction with your
            web browser. Once you enter your credentials and
            give authorization, you will be redirected to
            a url.  Paste that url you were directed to to
            complete the authorization.
        ''')

        auth_url = sp_oauth.get_authorize_url()
        #attempt to open the authorize url. This will redirect to our redirect page upon login
        try:
            # import webbrowser
            # webbrowser.open_new_tab(auth_url)
            #return HttpResponse("OPENED: " + str(auth_url))
            return HttpResponseRedirect(str(auth_url))

        except:
            return HttpResponse("FAILED")

def finish_spot_auth(request):
    c = connections['default'].cursor()
    client_id = '327541285c7343afbf4822dc9d30ef7f'
    client_secret = '713dbe89b2ea4bd382fb0a7b366a63bb'
    redirect_uri = 'http://smalldata411.web.illinois.edu/redirect'
    cache_path = None
    username = 'sahil5'          #hardcoded now...change for later
    scope = 'user-library-read'
    sp_oauth = oauth2.SpotifyOAuth(client_id, client_secret, redirect_uri, scope=scope, cache_path=cache_path)
    response = str(request.build_absolute_uri())
    code = sp_oauth.parse_response_code(response)
    token_info = sp_oauth.get_access_token(code)
    token = token_info['access_token']
    # # Auth'ed API request
    client_credentials_manager = SpotifyClientCredentials(client_id = client_id, client_secret= client_secret)
    
    if token:
        insert_spotify(request.user.id, token)
        sp = spotipy.Spotify(auth=token, client_credentials_manager=client_credentials_manager)
        results = sp.current_user_playlists(limit=50) #max limit is fifty songs...use paging to scroll through results
        results = results["items"]
        playlist = dict()
        for keys in results:
            playlist[keys["name"]] = keys["id"]
        

        for playlist_name in playlist:
            song = sp.user_playlist_tracks("sahils", playlist_id = playlist[playlist_name], limit=50)
            tracks = song['items']
            while song['next']:
                song = sp.next(song)
                tracks.extend(song['items']) #tracks is a list
            
            values = list()
            songID = 0
            
            #raise Exception('maxsongid is {}'.format(maxsongid))
            try:
                c.execute("SELECT max(UniqueSongID) FROM TopSongsMeta")
                maxsongid = c.fetchall()[0][0]
    
                if (maxsongid != 0):
                    songID = maxsongid +1
            except:
                songID = 0
            #if ()
            coun = 0
            
            for track in tracks:
                song = track['track']
                name = song['name']
                id = song['id']
                #quote in name braks errything
                artist  = song['artists'][0]['name']
                if "'" in name or "'" in artist:
                    continue
                #check if song, artist, and service combination already exist in the DB
                #command  = "SELECT UniqueSongID FROM TopSongsMeta WHERE artist = \"" + str(artist) + "\" and title = \"" + str(name) +"\""
                command = "SELECT UniqueSongID FROM TopSongsMeta WHERE artist = \' " + str(artist) + "\' and title = \'" + str(name) + "\' and UserId = " + str(request.user.id)
                c.execute(command, [])
                rows = c.fetchall()
                if(len(rows) != 0):
                    songID = songID + 1
                    coun+=1
                    continue
                tuple = "("
                current_user_id = str(request.user.id)
                tuple  += "{}, ".format(current_user_id)
                tuple += "'Spotify', "
                tuple += "'" + str(artist.replace(",","")) +"', "
                tuple += "'" + str(name.replace(",","")) +"', "
                tuple += str(songID) + ", "
                tuple += "'" + str(playlist_name) + "', "
                tuple += "'" + str(id) + "'"
                tuple += ")"
                values.append(tuple)
                songID = songID + 1

            if(len(values) != 0):
                insert_a_lot('TopSongsMeta', '(UserID, Service, Artist, Title, UniqueSongID, Playlist, SpotifySongID)', values)
        return HttpResponseRedirect("http://smalldata411.web.illinois.edu")
    else:
        return HttpResponse("ERROR")
   # return HttpResponse(str(token_info))
    
    
    

def insert_spotify(userId, token):
    c = connections['default'].cursor()
    sql_syn = "INSERT INTO Spotify (UserID, Token) VALUES "
    sql_syn += "( {}, \'{}\')".format(userId, token) 
    #if it exits, update, if it doesn't create a new row 
    if(exists_in_spotify(userId)):
        sql_syn_2 = "DELETE FROM Spotify WHERE UserID = \'{}\'".format(userId)
        c.execute(sql_syn_2,[])
    c.execute(sql_syn,[])
    
def insert_user(userId, userName):
    c = connections['default'].cursor()
    sql_syn = "INSERT INTO Users (UserID, Username) VALUES "
    sql_syn += "( {}, \'{}\')".format(userId,userName)  
    if(not exists_in_users(userName)):
        c.execute(sql_syn,[])

# SAHIL, I made the 'insert_a_lot' function for you. 
# Pass it the name of the table as a string (e.g. 'Users'), the attributes as
# a string (e.g. '(UserID, FirstName, LastName, NumberOfAccounts)') and the 
# values as a list of strings... however make sure to put the string values in
# single quotes inside of the string (otherwise it won't work)!! E.g. : 
#  lst = ["(4, 'Avery','Apple', 20)", "(5, 'Sandra', 'Strawberry', 10)", "(6, 'Ben', 'Banana', 3)"]
# before inserting, verify that data does not already exists in the DB

def insert_a_lot(tableName,tableAttributes,values):
    c = connections['default'].cursor()
    sql_syn = "INSERT INTO "
    lendebug = []
    sql_syn+= tableName + " " + tableAttributes +  " VALUES "
    for i in range(len(values)):
        readstr = values[i].replace(")","")
        readstr = readstr.replace("(","")
        readstr = readstr.split(",")
        debug = exists_in_topsongsmeta(readstr[0],readstr[1],readstr[2],readstr[3])
        lendebug.append(len(debug))
        if( len(debug) is 0 ):
            sql_syn += values[i]
            if(i< len(values)-1):
                sql_syn+=","
    if sql_syn[len(sql_syn)-1] is ',':
        sql_syn = sql_syn[:len(sql_syn)-1] +';'
    else:
        sql_syn += ";"
    #raise Exception('{}'.format(sql_syn))
    if (sql_syn[-2] == ' '):
        return
    c.execute(sql_syn,[])

#Checks if username exists

def exists_in_spotify(UserID):
    c = connections['default'].cursor()
    sql_syn = "SELECT * FROM Spotify WHERE UserID = \'{}\'".format(UserID)
    c.execute(sql_syn,[])
    vals = c.fetchall()
    return (len(vals) != 0) 
    
def exists_in_users(Username):
    c = connections['default'].cursor()
    sql_syn = "SELECT * FROM Users WHERE Username = \'{}\'".format(Username)
    c.execute(sql_syn,[])
    vals = c.fetchall()
    return (len(vals) != 0) 
    
def exists_in_topsongsmeta(UserID, Service, Artist, Title):
    print(UserID, Service, Artist, Title)
    c = connections['default'].cursor()
    sql_syn = "SELECT (Artist) FROM TopSongsMeta WHERE " + "UserID = " \
    + UserID + " and Service = " + Service +\
    " and Artist = " + Artist + " and Title =" + Title 
    print(sql_syn)
    c.execute(sql_syn,[])
    vals = c.fetchall()
    return vals
    
# INSET INTO TopSongsMeta (UserID, Service, Artist, Title, UniqueSongID)


def searchQuery(request):
    #How to connect to the database and display 
    #Build an HTML page response
    search_value = request.GET.get("SearchVal","") 
    search_table = request.GET.get("SearchTable","")
    search_attributes = request.GET.get("Attributes","")
    c = connections['default'].cursor()
    sql_syn = ""
    if(',' in search_attributes):
        #sql_syn = "SELECT * FROM " + search_table + " WHERE " + search_value + " IN " + search_attributes + ";"
        sql_syn = "SELECT * FROM " + search_table +  " WHERE %s IN " + search_attributes + ";"
    else:
        #sql_syn = "SELECT * FROM " + search_table + " WHERE " + search_attributes + " = " + search_value + ";"   
        sql_syn = "SELECT * FROM " +search_table+  " WHERE " +search_attributes+ "= %s;"
    
    response = HttpResponse("Failure")
    try:
        c.execute(sql_syn,[search_value])
        rows = c.fetchall()
        if (len(rows) != 0):
            response = HttpResponse(rows)
        response = HttpResponse("No Results")
    except:
        response = HttpResponse("EXEPTNo Results")
            
    return response
    

    
def insertQuery(request):
    insert_table = request.GET.get("InsertTable","")
    insert_attributes = request.GET.get("InsertAttributes","")
    insert_values = request.GET.get("InsertValues")
    c = connections['default'].cursor()
    sql_syn = "INSERT INTO " + insert_table + " " + insert_attributes + " VALUES " + insert_values + ";" 
    c.execute(sql_syn,[])
    rows = c.fetchall()
    response = HttpResponse("Ran\n" + sql_syn + "successfully")
    
    return response
    
def graphOne(request):
    return render(request, 'charts.html',{})

class HomeView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'charts.html',{})

def get_data(request, *args, **kwargs):
    # GET DATA HERE YOU WANT TO DISPLAY 
    data = {
        "Sales":100,
        "Customers":10, 
    }
    return JsonResponse(data)

def updateQuery(request):
    c = connections['default'].cursor()
    update_table = request.GET.get("UpdateTable","")
    update_attributes = request.GET.get("UpdateAttributes","")
    update_values = request.GET.get("UpdateValues","")
    update_condition = request.GET.get("UpdateCondition","")
    
    sql_syn = "UPDATE " + update_table + " SET " + update_attributes + " = " + update_values + " WHERE " + update_condition
    
    c.execute(sql_syn,[])
    response = HttpResponse(sql_syn + "SUCCESS")
    return response 

def deleteQuery(request):
    c = connections['default'].cursor()
    delete_table = request.GET.get("DeleteTable","")
    delete_attributes = request.GET.get("DeleteAttributes","")
    delete_condition = request.GET.get("DeleteCondition","")
    
    sql_syn = "DELETE FROM " + delete_table + " WHERE " + delete_attributes + delete_condition

    c.execute(sql_syn,[])
    response = HttpResponse(sql_syn + "SUCCESS")
    return response     
    
def get_user_recommendations(request):
    if (request.user.id is None):
        return []
    client_credentials_manager = SpotifyClientCredentials('327541285c7343afbf4822dc9d30ef7f', client_secret='713dbe89b2ea4bd382fb0a7b366a63bb')
    spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    c = connections['default'].cursor()
    current_usr = request.user.id
    sql_syn = 'SELECT SpotifySongID FROM TopSongsMeta WHERE UserID = ' + str(current_usr)
    c.execute(sql_syn, [])
    rows = c.fetchall()
    if(len(rows) == 0):
        return []
    querylist = []
    for i in range(len(rows)):
        querylist.append(rows[i])
    shuffle(querylist)    #recommend based on 20 random songs in the users database
    querylist = querylist[0:20]
    recommended = []
    for i in range(0,len(querylist),5):
        songs = []
        songIds = querylist[i:min(i+5,len(querylist))]
        for i in range(0,len(songIds),1):
            songIds[i] = songIds[i][0]
        if (len(songIds) == 0):
            break
        try:
            recs = spotify.recommendations(seed_tracks=songIds, limit = 20)      #modify limit to control how many recommendations are returned per 5 seeds
        except:
            return []
        recs=recs['tracks']
        for track in recs:
            url = track['external_urls']['spotify']
            songName = track['name']
            artist = track['artists'][0]['name']
            recommended.append((songName, artist,url))
    shuffle(recommended)
    recommended = recommended[0:min(20,len(recommended))]
    #raise Exception("check songIds")
    return recommended

    
def get_master_scatterplotdata(request):
    datapoints = []
    client_credentials_manager = SpotifyClientCredentials('327541285c7343afbf4822dc9d30ef7f', client_secret='713dbe89b2ea4bd382fb0a7b366a63bb')
    spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    c = connections['default'].cursor()
    current_usr = request.user.id
    sql_syn = 'SELECT SpotifySongId,Title,Artist FROM TopSongsMeta WHERE UserId = ' + str(current_usr)
    c.execute(sql_syn, [])
    rows = c.fetchall()
    if(len(rows) == 0):
        return HttpResponse("Empty query result")
    querylist = []
    
    for i in range(len(rows)):
        querylist.append(rows[i])

    shuffle(querylist)    #recommend based on 50 random songs in the users database
    songIds = []
    names = []
    for i in range(len(querylist)):
        songIds.append(querylist[i][0])
        names.append(querylist[i][1] + " by " + querylist[i][2])
    for i in range(len(songIds)):
        if songIds[i] is None:
            del songIds[i]
    features = spotify.audio_features(songIds[0:50]) #features is a list of dictionaries
    for i in range(len(features)):
        track=  features[i]
        nam = names[i]
        if track is None:
            continue
        danceability = track['danceability']
        energy = track['energy']
        tempo = track['tempo']
        loudness = track['loudness']
        speechiness = track['speechiness']
        instrumentalness = track['instrumentalness']
        
        x = (tempo*energy) + (tempo*danceability)
        y = -((10*loudness*speechiness) - (10*loudness*instrumentalness))
        datapoints.append((x,y,nam))

    return datapoints    #raise Exception("check features")
            
class ChartData(APIView):
    """
    From https://www.django-rest-framework.org/
    """
    authentication_classes = []
    permission_classes = []
    
    def get(self, request, format=None):
        bob = request.user.id
        default_data = ((bob,0))
        data = {
            "labels":[],
            "default_data":default_data, 
        }
        return Response(data)
 
        