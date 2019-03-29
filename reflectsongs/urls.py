"""reflectsongs URL Configuration

"""
from django.urls import path

from reflectsongs.views import HomeView, SongView

urlpatterns = [
    path('', HomeView.as_view()),
    path('s/<slug:song_slug>/', SongView.as_view(), name='song-view'),
]
