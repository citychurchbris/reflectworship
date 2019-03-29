from django.shortcuts import get_object_or_404, render
from django.views import View

from reflectsongs.models import Song
from reflectsongs.utils import yt_embed


class HomeView(View):

    def get(self, request):
        return render(
            request,
            'reflectsongs/index.html',
        )


class SongView(View):

    def get(self, request, song_slug):
        song = get_object_or_404(Song, slug=song_slug)
        context = {
            'song': song,
        }
        if song.youtube_url:
            context['embed_code'] = yt_embed(song.youtube_url)

        return render(
            request,
            'reflectsongs/song.html',
            context=context,
        )
