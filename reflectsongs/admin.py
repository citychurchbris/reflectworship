from django import forms
from django.contrib import admin
from django.db.models import Count, Max, Q
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from easy_select2 import Select2Multiple

from reflectsongs.filters import SiteSongFilter
from reflectsongs.models import Setlist, Site, Song


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    pass


class SetlistForm(forms.ModelForm):

    class Meta:
        widgets = {
            'songs': Select2Multiple(),
        }


@admin.register(Setlist)
class SetlistAdmin(admin.ModelAdmin):
    form = SetlistForm
    list_display = (
        '__str__',
        'site',
        'date',
        'name',
    )

    list_filter = (
        'site',
    )


@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    search_fields = (
        'title',
    )
    list_display = (
        'title',
        'play_count',
        'last_played',
    )
    list_filter = (
        SiteSongFilter,
    )

    readonly_fields = (
        'play_count',
        'last_played',
        'setlist_display',
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)

        # Filter setlist count by site
        siteid = request.GET.get('site')
        if siteid:
            sitefil = Q(setlists__site=siteid)
        else:
            sitefil = None

        queryset = queryset.annotate(
            _setlist_count=Count('setlists', distinct=True, filter=sitefil),
            _last_played=Max("setlists__date", filter=sitefil),
        )
        return queryset

    def play_count(self, obj):
        return obj._setlist_count
    play_count.admin_order_field = '_setlist_count'

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


admin.site.site_header = 'Reflect Worship Database'
