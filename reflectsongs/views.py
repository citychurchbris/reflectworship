import datetime

from django.db.models import Count, Max, Min
from django.shortcuts import get_object_or_404, render
from django.views import View

from dateutil.relativedelta import relativedelta

from reflectsongs.models import Site, Song
from reflectsongs.utils import yt_embed


class HomeView(View):

    def get(self, request):
        queryset = Song.objects.all()
        queryset = queryset.annotate(
            setlist_count=Count('setlists', distinct=True),
            _first_played=Min("setlists__date"),
            _last_played=Max("setlists__date"),
        )

        # Last 6 months of top songs
        today = datetime.date.today()
        topsongs = queryset.filter(
            _last_played__gt=today - relativedelta(months=6),
        ).order_by('-setlist_count')[:10]

        # No date filter on newest
        newsongs = queryset.filter(
            _first_played__isnull=False
        ).order_by('-_first_played')[:10]

        return render(
            request,
            'reflectsongs/index.html',
            context={
                'topsongs': topsongs,
                'newsongs': newsongs,
                'sites': Site.objects.all(),
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
