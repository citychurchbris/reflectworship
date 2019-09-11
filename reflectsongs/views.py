import datetime

from django.db.models import Count, Max, Min, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import DetailView, ListView

from dateutil.relativedelta import relativedelta

from reflectsongs.models import ChordResource, Setlist, Site, Song
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
    return songs.order_by('-setlist_count')


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


def has_photo(item):
    return bool(item.photo)


def photo_filter(items):
    return list(filter(has_photo, items))


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
                'topsongs_photos': photo_filter(topsongs),
                'newsongs': newsongs[:self.nsongs],
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


class Search(SongList):

    def get_search_query(self):
        return self.request.GET.get('q', '')

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.get_search_query()
        if search_query:
            queryset = queryset.filter(title__search=search_query)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.get_search_query()
        return context


class SetlistList(ListView):

    model = Setlist
    context_object_name = 'setlists'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
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
        context['topsongs_photos'] = photo_filter(topsongs)
        context['newsongs'] = newsongs[:10]
        context['newsongs_photos'] = photo_filter(newsongs)
        context['all_age'] = all_age
        context['all_age_photos'] = photo_filter(all_age)
        return context


class DownloadResource(View):

    def get(self, request, pk):
        resource = get_object_or_404(
            ChordResource,
            pk=pk,
        )
        return redirect(resource.attachment.url)
