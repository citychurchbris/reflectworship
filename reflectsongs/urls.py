"""reflectsongs URL Configuration

"""
from django.urls import path

from reflectsongs.views import HomeView, SongList, SongView

urlpatterns = [
    path('', HomeView.as_view()),
    path('song/<slug:song_slug>/', SongView.as_view(), name='song-view'),
    path('songs/', SongList.as_view(), name='song-list'),
]
