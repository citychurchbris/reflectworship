"""reflectsongs URL Configuration

"""
from django.urls import path

from reflectsongs.views import (HomeView, SetlistList, SetlistView, SiteList,
                                SiteView, SongList, SongView)

urlpatterns = [
    path('', HomeView.as_view()),

    # Setlists
    path('setlists/<pk>/', SetlistView.as_view(), name='setlist-view'),
    path('setlists/', SetlistList.as_view(), name='setlist-list'),

    # Songs
    path('songs/<slug:song_slug>/', SongView.as_view(), name='song-view'),
    path('songs/', SongList.as_view(), name='song-list'),

    # Sites
    path('sites/<slug:slug>/', SiteView.as_view(), name='site-view'),
    path('sites/', SiteList.as_view(), name='site-list'),

]
