"""reflectsongs URL Configuration

"""
from django.urls import path
from django.views.generic import TemplateView

from reflectsongs.views import (DownloadResource, HomeView, Search,
                                SetlistList, SetlistView, SiteList, SiteView,
                                SongList, SongPresentation, SongView, Words)

urlpatterns = [
    path('robots.txt', TemplateView.as_view(
        template_name="reflectsongs/robots.txt")),

    path('', HomeView.as_view()),

    # Setlists
    path('setlists/<pk>/', SetlistView.as_view(), name='setlist-view'),
    path('setlists/', SetlistList.as_view(), name='setlist-list'),

    # Songs
    path('songs/<slug:song_slug>/', SongView.as_view(), name='song-view'),
    path('songs/<slug:song_slug>/show', SongPresentation.as_view(),
         name='song-show'),
    path('songs/', SongList.as_view(), name='song-list'),

    # Downloads
    path('download/<pk>/', DownloadResource.as_view(), name='download'),

    # Sites
    path('sites/<slug:slug>/', SiteView.as_view(), name='site-view'),
    path('sites/', SiteList.as_view(), name='site-list'),

    # Search
    path('search', Search.as_view(), name='search'),

    # Stats
    path('words', Words.as_view(), name='words'),

]
