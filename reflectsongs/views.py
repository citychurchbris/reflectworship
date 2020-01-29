import datetime

from django.db import connection
from django.db.models import Count, Max, Min, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import DetailView, ListView

from dateutil.relativedelta import relativedelta

from reflectsongs.models import ChordResource, Setlist, Site, Song, Theme
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
        from_date=today - relativedelta(months=months)
    ).filter(setlist_count__gte=1)
    return songs.order_by('-setlist_count', 'title')


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
    ).order_by('-_first_played')
    return newsongs


class HomeView(View):

    nsongs = 10

    def get(self, request):
        # Last 6 months of top songs
        topsongs = get_top_songs()
        newsongs = get_newest_songs()
        featured = Song.objects.filter(featured=True)

        # Add featured to top of new songs
        newsongs = list(featured) + list(newsongs.filter(featured=False))

        # All age
        all_age = topsongs.filter(all_age=True)

        return render(
            request,
            'reflectsongs/index.html',
            context={
                'all_age': all_age[:self.nsongs],
                'topsongs': topsongs[:self.nsongs],
                'newsongs': newsongs[:self.nsongs],
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
            'downloads': song.downloads.all(),
        }
        if song.youtube_url:
            context['embed_code'] = yt_embed(song.youtube_url)

        return render(
            request,
            'reflectsongs/song.html',
            context=context,
        )


class SongList(ListView):

    model = Song
    context_object_name = 'songs'
    paginate_by = 10

    date_mapping = {
        '12m': 12,
        '6m': 6,
    }

    def get_range_query(self):
        return self.request.GET.get('range', '')

    def get_queryset(self):
        date_range = self.get_range_query()
        months = self.date_mapping.get(date_range, 999)
        queryset = get_top_songs(site=None, months=months)
        return queryset


class Search(SongList):

    def get_search_query(self):
        return self.request.GET.get('q', '')

    def get_theme_query(self):
        return self.request.GET.get('theme', '')

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.get_search_query()
        theme_query = self.get_theme_query()
        if search_query:
            queryset = queryset.filter(title__search=search_query)
        if theme_query:
            queryset = queryset.filter(themes__slug=theme_query)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query_data = self.get_search_query()
        theme_query = self.get_theme_query()
        if theme_query:
            theme = Theme.objects.get(slug=theme_query)
            query_data = f"Theme: {theme}"
        context['search_query'] = query_data
        return context


class SetlistList(ListView):

    model = Setlist
    context_object_name = 'setlists'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        # Don't include setlists with no songs
        queryset = queryset.annotate(song_count=Count('songs')).filter(
            song_count__gte=1,
        )
        filter_song = self.get_filter_song()
        if filter_song:
            queryset = queryset.filter(songs=filter_song)
        return queryset

    def get_filter_song(self):
        songslug = self.request.GET.get('song', '')
        if songslug:
            try:
                return Song.objects.get(slug=songslug)
            except Song.DoesNotExist:
                return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filter_song = self.get_filter_song()
        context['filter_song'] = filter_song
        context['title'] = filter_song and 'Setlists' or 'All Setlists'
        return context


class SetlistView(DetailView):

    model = Setlist


class SiteList(ListView):

    model = Site
    context_object_name = 'sites'


class SiteView(DetailView):

    model = Site

    def get_context_data(self, **kwargs):
        site = kwargs.get('object')
        context = super().get_context_data(**kwargs)
        topsongs = get_top_songs(site=site)
        newsongs = get_newest_songs(site=site)
        all_age = get_top_songs(site=site, months=12).filter(all_age=True)
        context['topsongs'] = topsongs[:10]
        context['newsongs'] = newsongs[:10]
        context['all_age'] = all_age
        return context


class DownloadResource(View):

    def get(self, request, pk):
        resource = get_object_or_404(
            ChordResource,
            pk=pk,
        )
        return redirect(resource.attachment.url)


class Stats(View):

    def get(self, request):
        sql = (
            "SELECT * FROM ts_stat("
            "'SELECT to_tsvector(''simple'', lyrics) FROM reflectsongs_song')"
        )
        with connection.cursor() as cursor:
            cursor.execute(sql)
            data = cursor.fetchall()

        COMMON_WORDS = (
            "the",
            "and",
            "of",
            "is",
            "to",
            "in",
            "a",
            "be",
            "it",
        )

        words = []
        for item in data:
            word, ndocs, nwords = item
            if word in COMMON_WORDS:
                continue
            words.append({
                'word': word,
                'ndocs': ndocs,
                'nwords': nwords,
            })
        words_by_count = sorted(words,
                                key=lambda x: x['nwords'], reverse=True)
        words_by_song = sorted(words,
                               key=lambda x: x['ndocs'], reverse=True)

        context = {
            'words_by_count': words_by_count,
            'words_by_song': words_by_song,
        }

        return render(
            request,
            'reflectsongs/stats.html',
            context=context,
        )
