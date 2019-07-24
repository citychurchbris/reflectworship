import datetime

from django.core.paginator import Paginator
from django.db.models import Count, Max, Min, Q
from django.shortcuts import get_object_or_404, render
from django.views import View
from django.views.generic import DetailView, ListView

from dateutil.relativedelta import relativedelta

from reflectsongs.models import Setlist, Site, Song
from reflectsongs.utils import yt_embed


def get_song_queryset(site=None, from_date=None):
    """ Get a reusable song queryset """
    queryset = Song.objects.all()
    if site is not None:
        sitefil = Q(setlists__site=site)
    else:
        sitefil = Q()

    if from_date:
        datefil = Q(setlists__date__gte=from_date)
    else:
        datefil = Q()

    queryset = queryset.annotate(
        setlist_count=Count('setlists', distinct=True,
                            filter=sitefil & datefil),
        _first_played=Min("setlists__date", filter=sitefil),
        _last_played=Max("setlists__date", filter=sitefil),
    )
    return queryset


def get_top_songs(site=None, months=6):
    """ Last x months of most played songs """
    today = datetime.date.today()
    songs = get_song_queryset(
        site=site,
        from_date=today - relativedelta(months=6)
    )
    return songs.order_by('-setlist_count')[:10]


def get_newest_songs(site=None, written_since=None):
    """ Newest songs that were written since x """
    if written_since is None:
        today = datetime.date.today()
        written_since = today.year - 3

    songs = get_song_queryset(site=site)
    newsongs = songs.filter(
        _first_played__isnull=False
    ).filter(
        copyright_year__gt=written_since
    ).order_by('-_first_played')[:10]
    return newsongs


def has_photo(item):
    return bool(item.photo)


def photo_filter(items):
    return list(filter(has_photo, items))


class HomeView(View):

    def get(self, request):
        # Last 6 months of top songs
        topsongs = get_top_songs()
        newsongs = get_newest_songs()

        return render(
            request,
            'reflectsongs/index.html',
            context={
                'topsongs': topsongs,
                'topsongs_photos': photo_filter(topsongs),
                'newsongs': newsongs,
                'newsongs_photos': photo_filter(newsongs),
                'sites': Site.objects.all(),
            }
        )


class SongView(View):

    def get(self, request, song_slug):
        sites = Site.objects.all()
        song = get_object_or_404(Song, slug=song_slug)

        # Calculate last played date for each site
        last_played_sites = []
        for site in sites:
            last_played_sites.append({
                'site': site,
                'last_played': song.last_played_site(site),
            })
        last_played_sites.sort(
            key=lambda x: x['last_played'] and x['last_played'].date
            or datetime.date.min,
            reverse=True,
        )

        context = {
            'song': song,
            'last_played_sites': last_played_sites,
        }
        if song.youtube_url:
            context['embed_code'] = yt_embed(song.youtube_url)

        return render(
            request,
            'reflectsongs/song.html',
            context=context,
        )


class SongList(View):

    def get(self, request):
        song_list = Song.objects.all().order_by('title')
        paginator = Paginator(song_list, 10)

        page = request.GET.get('page')
        songs = paginator.get_page(page)
        return render(request, 'reflectsongs/song_list.html', {'songs': songs})


class SetlistList(ListView):

    model = Setlist
    context_object_name = 'setlists'
    paginate_by = 10


class SetlistView(DetailView):

    model = Setlist
