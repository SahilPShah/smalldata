import requests
from django.http import HttpResponse
from django.db import connections
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import urllib3
import json
import spotipy
import spotipy.oauth2 as oauth2
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util
CLIENT_SECRETS_FILE = "/home/smalldata411/smalldata/auth/client_id.json"
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'
YOUTUBEBASE = "https://www.youtube.com/watch?v="

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
from django.http import HttpResponseRedirect

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

def spotsearch(name):
    #search field\
    client_credentials_manager = SpotifyClientCredentials('327541285c7343afbf4822dc9d30ef7f', client_secret='713dbe89b2ea4bd382fb0a7b366a63bb')
    spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    results = spotify.search(q='track:' + name, type='track')
    items = results['tracks']['items']
    #print (results['tracks']['items'])
    for element in items:
        return element['name'],element['artists'][0]['name'],element['id']
    return None,None,None

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

def ytredirect(request):
    userid = request.user.id
    c = connections['default'].cursor()
    sql_syn = "SELECT State FROM Youtube WHERE UserID={}".format(userid)
    c.execute(sql_syn,[])
    state = c.fetchall()[0][0]
    #raise Exception("{}".format(state))
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
    CLIENT_SECRETS_FILE, scopes=["https://www.googleapis.com/auth/youtube.readonly","https://www.googleapis.com/auth/youtube.force-ssl"], state=state)
    flow.redirect_uri = "https://smalldata411.web.illinois.edu/youtube-redirect"
    flow.fetch_token(authorization_response=request.build_absolute_uri())
    
    #TODO: MAKE A FUNCTION THAT SERIALIZES CREDENTIALS, AND THEN STORES IT IN THE DATABASE. THEN STORE SONGS IN DATABASE AS REDIRECTED TO HOOME PAGE
    credentials = json.dumps(credentials_to_dict(flow.credentials))
    
    #raise Exception("debug")
    #store token in db
    if(exists(userid)):
        #update
         c = connections['default'].cursor()
         sql_syn = "UPDATE Youtube SET Token = \'{}\' WHERE UserID = {}".format(credentials,userid)
         c.execute(sql_syn,[])
    else:
        #insert
        c = connections['default'].cursor()
        sql_syn = "INSERT INTO Youtube (UserID, Token, State) VALUES( {},'' ,\'{}\')".format(userid,state)
        c.execute(sql_syn,[])
    
    ## GET VIDEOS FROM YOUTUBE, AND THEN SEARCH FOR THEM ON SPOTIFY, IF RESULT IS FOUND USE IT, OTHERWISE TRY TO GET GENRE USING FREEBASE, OTHERWISE IGNORE SONG
    client = googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, credentials=flow.credentials)
    playlists = getPlaylistsFromYoutube(client,flow.credentials)
    playlist_objects = playlists['items']
    foundid = 0
    for playlist_object in playlist_objects:
        if (playlist_object['snippet']['localized']['title'] == 'smalldata'):
            foundid = playlist_object['id']
    if (foundid is 0):
        raise Exception("playlist titled smalldata not found")
        
    list = playlist_items_list_by_playlist_id(client,
    part='snippet,contentDetails',
    maxResults=25,
    playlistId=foundid)
    ids = []
    for video in list['items']:
        id = video['contentDetails']['videoId']
        ids.append(id)
    ids = str(ids)[1:-1].replace("'","").replace(" ","")
    
    posturl = "http://music-in-this-yt-vid.com/?ids={}".format(ids)
    http = urllib3.PoolManager()
    response = http.request('GET',posturl).data
    
    
    listofsongs = json.loads(response.decode('utf-8'))['response']
    
    spotsongs = []
    for song in listofsongs:
        spotsong, spotartist,id = spotsearch(song)
        if (spotsong is not None):
            spotsongs.append((spotsong,spotartist,id))
    
    
    try:
        c.execute("SELECT max(UniqueSongID) FROM TopSongsMeta")
        maxsongid = c.fetchall()[0][0]

        if (maxsongid != 0):
            songID = maxsongid +1
    except:
        songID = 0
    #if ()
    values = []
    for track in spotsongs:
        name = track[0]
        #quote in name braks errything
        artist  = track[1]
        if "'" in name or "'" in artist:
            continue
        #check if song, artist, and service combination already exist in the DB
        #command  = "SELECT UniqueSongID FROM TopSongsMeta WHERE artist = \"" + str(artist) + "\" and title = \"" + str(name) +"\""
        command = "SELECT UniqueSongID FROM TopSongsMeta WHERE artist = \' " + str(artist) + "\' and title = \'" + str(name) + "\'"
        c.execute(command, [])
        rows = c.fetchall()
        if(len(rows) != 0):
            songID = songID + 1
            continue
        id = track[2]
        tuple = "("
        current_user_id = str(request.user.id)
        tuple  += "{}, ".format(current_user_id)
        tuple += "'Youtube', "
        tuple += "'" + str(artist.replace(",","")) +"', "
        tuple += "'" + str(name.replace(",","")) +"', "
        tuple += str(songID) + ", "
        tuple += "'" + str("smalldata") + "',"
        tuple += "'" + str(id) + "'"
        tuple += ")"
        values.append(tuple)
        songID = songID + 1
    if(len(values) != 0):
        insert_a_lot('TopSongsMeta', '(UserID, Service, Artist, Title, UniqueSongID, Playlist, SpotifySongID)', values)
    
    return HttpResponseRedirect("http://smalldata411.web.illinois.edu/")


    
def videos_list_by_id(client, **kwargs):
  # See full sample for function
  kwargs = remove_empty_kwargs(**kwargs)

  response = client.videos().list(
    **kwargs
  ).execute()

  return response
  
  
# Remove keyword arguments that are not set
def remove_empty_kwargs(**kwargs):
  good_kwargs = {}
  if kwargs is not None:
    for key, value in kwargs.items():
      if value:
        good_kwargs[key] = value
  return good_kwargs
  
def playlist_items_list_by_playlist_id(client, **kwargs):
  # See full sample for function
  kwargs = remove_empty_kwargs(**kwargs)

  response = client.playlistItems().list(
    **kwargs
  ).execute()

  return response
  
def getPlaylistsFromYoutube(client, credentials):
    playlists = client.playlists().list(mine= True, part = 'snippet').execute();
    return playlists
def ytlogin(request):
    
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=["https://www.googleapis.com/auth/youtube.readonly","https://www.googleapis.com/auth/youtube.force-ssl"])
    flow.redirect_uri = "https://smalldata411.web.illinois.edu/youtube-redirect"
    
    authorization_url, state = flow.authorization_url(
      # Enable offline access so that you can refresh an access token without
      # re-prompting the user for permission. Recommended for web server apps.
      access_type='offline',
      # Enable incremental authorization. Recommended as a best practice.
      include_granted_scopes='true')
      
    userid = request.user.id
    if(exists(userid)):
        #update
         c = connections['default'].cursor()
         sql_syn = "UPDATE Youtube SET State = \'{}\' WHERE UserID = {}".format(state,userid)
         c.execute(sql_syn,[])
    else:
        #insert
        c = connections['default'].cursor()
        sql_syn = "INSERT INTO Youtube (UserID, Token, State) VALUES( {},'' ,\'{}\')".format(userid,state)
        c.execute(sql_syn,[])
    return HttpResponseRedirect(authorization_url)
    
def exists(userid):
    c = connections['default'].cursor()
    sql_syn = "SELECT * FROM Youtube WHERE UserID = \'{}\'".format(userid)
    c.execute(sql_syn,[])
    vals = c.fetchall()
    return (len(vals) != 0) 
def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}