from django import forms
from django.contrib import admin
from django.db.models import Count, Max, Q
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from easy_select2 import Select2Multiple

from reflectsongs.filters import SiteSongFilter
from reflectsongs.models import ChordResource, Setlist, Site, Song


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):

    prepopulated_fields = {"slug": ("name",)}


class SetlistForm(forms.ModelForm):

    class Meta:
        widgets = {
            'songs': Select2Multiple(),
        }


@admin.register(Setlist)
class SetlistAdmin(admin.ModelAdmin):
    form = SetlistForm
    search_fields = (
        'name',
    )
    date_hierarchy = 'date'
    list_display = (
        '__str__',
        'site',
        'date',
        'name',
        'nsongs',
    )
    list_filter = (
        'site',
        'date',
    )

    def nsongs(self, obj):
        return obj.songs.count()
    nsongs.short_description = 'Songs'


class ChordResourceInline(admin.TabularInline):
    model = ChordResource


@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    inlines = (
        ChordResourceInline,
    )
    search_fields = (
        'title',
        'authors',
    )
    list_display = (
        'title',
        'authors',
        'ccli_number',
        'copyright_year',
        'play_count',
        'last_played',
        'has_video',
    )
    list_filter = (
        SiteSongFilter,
        'setlists__date',
        'all_age',
        'featured',
    )

    readonly_fields = (
        'slug',
        'songselect_link',
        'play_count',
        'last_played',
        'setlist_display',
        'last_sync',
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)

        # Filter setlist count by site
        siteid = request.GET.get('site')
        if siteid:
            sitefil = Q(setlists__site=siteid)
        else:
            sitefil = Q()

        setlistdate_max = request.GET.get('setlists__date__lt')
        setlistdate_min = request.GET.get('setlists__date__gte')
        if setlistdate_max:
            datefil = Q(setlists__date__lte=setlistdate_max,
                        setlists__date__gte=setlistdate_min)
        else:
            datefil = Q()

        queryset = queryset.annotate(
            _setlist_count=Count('setlists', distinct=True,
                                 filter=sitefil & datefil),
            _last_played=Max("setlists__date", filter=sitefil),
        )
        return queryset

    def play_count(self, obj):
        return obj._setlist_count
    play_count.admin_order_field = '_setlist_count'
    play_count.short_description = 'Plays'

    def last_played(self, obj):
        return obj._last_played
    last_played.admin_order_field = '_last_played'

    def setlist_display(self, obj):
        listing = ""
        for setlist in obj.setlists.all():
            url = reverse('admin:reflectsongs_setlist_change',
                          args=(setlist.id, ))
            listing += format_html(
                "<a href='{}'>{}</a><br />",
                url,
                str(setlist),
            )
        return mark_safe(listing)
    setlist_display.short_description = 'Setlists'

    def has_video(self, obj):
        return bool(obj.youtube_url)
    has_video.short_description = 'Video'
    has_video.boolean = True


admin.site.site_header = 'Reflect Worship Database'
