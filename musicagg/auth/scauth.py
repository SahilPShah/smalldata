import requests
import soundcloud
from . import applemusicclient
from django.http import HttpResponse
from django.http import HttpResponseRedirect

def sclogin(request):
    sc = soundcloud.Client(client_id= '63d1b7fd97ed4759b2edf0c2568d12ad',
                            client_secret= '5071a56551a9120f8992eebd074a0d3e',
                            redirect_uri= 'https://www.google.com/') #'http://smalldata411.web.illinois.edu')
    auth_url =  sc.authorize_url()
    return HttpResponseRedirect(str(auth_url))

    
