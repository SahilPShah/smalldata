"""aggserv_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from mainsite import views
from auth import ytauth
from django.urls import include 
from auth import scauth
from django.conf.urls import url 

urlpatterns = [
    path('', views.index, name='index'),
    path('graph/', views.renderGraph, name='renderGraph'),
    path('indexold/', views.indexold, name='indexold'),
    path('accounts/', include('django.contrib.auth.urls')), # auth related ish
    path('accounts/', include('accounts.urls')), #auth related ish again
    path('redirect/', views.finish_spot_auth, name='redirect'),
    path('youtube-redirect/', ytauth.ytredirect),
    path('admin/', admin.site.urls),
    path('spotify-login/', views.spotlogin),
    path('youtube-login/', ytauth.ytlogin),
    path('soundcloud-login/', scauth.sclogin),
    path('search-query/',views.searchQuery),
    path('insert-query/',views.insertQuery),
    path('update-query/',views.updateQuery),
    path('delete-query/',views.deleteQuery),
    url(r'^graph-one/$', views.HomeView.as_view(), name='home'), #graph-one/
    url(r'^api/data/$',views.get_data, name='chart-data'),
    url(r'^api/chart/data/$',views.ChartData.as_view()),
    
]
