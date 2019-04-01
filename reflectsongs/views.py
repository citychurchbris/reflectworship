from django.db.models import Count
from django.shortcuts import get_object_or_404, render
from django.views import View

from reflectsongs.models import Song
from reflectsongs.utils import yt_embed


class HomeView(View):

    def get(self, request):
        queryset = Song.objects.all()
        queryset = queryset.annotate(
            setlist_count=Count('setlists', distinct=True),
        )

        topsongs = queryset.order_by('-setlist_count')[:10]
        newsongs = queryset.order_by('-copyright_year')[:10]

        return render(
            request,
            'reflectsongs/index.html',
            context={
                'topsongs': topsongs,
                'newsongs': newsongs,
            }
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
