"""reflectsongs URL Configuration

"""
from django.urls import path

from reflectsongs.views import (HomeView, SetlistList, SetlistView, SongList,
                                SongView)

urlpatterns = [
    path('', HomeView.as_view()),

    # Songs
    path('songs/<slug:song_slug>/', SongView.as_view(), name='song-view'),
    path('songs/', SongList.as_view(), name='song-list'),

    # Setlists
    path('setlists/<pk>/', SetlistView.as_view(), name='setlist-view'),
    path('setlists/', SetlistList.as_view(), name='setlist-list')
]
