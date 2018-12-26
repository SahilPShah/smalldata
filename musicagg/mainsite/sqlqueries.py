from django.db import connections

def getSpotList(request):
    sql_syn = "SELECT Artist,Title,Playlist FROM TopSongsMeta WHERE UserID={} AND Service = \'Spotify\' LIMIT 30".format(request.user.id)
    c.execute(sql_syn,[])
    vals = c.fetchall()
    return vals
    
def getYoutubeList(request):
    sql_syn = "SELECT Artist,Title,Playlist FROM TopSongsMeta WHERE UserID={} AND Service = \'Youtube\' LIMIT 30".format(request.user.id)
    c.execute(sql_syn,[])
    vals = c.fetchall()
    return vals