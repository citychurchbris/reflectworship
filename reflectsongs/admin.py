from django.contrib import admin
from django.db.models import Count
from reflectsongs.models import Setlist, Site, Song


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    pass


@admin.register(Setlist)
class SetlistAdmin(admin.ModelAdmin):
    list_display = (
        '__str__',
        'site',
        'date',
    )

    list_filter = (
        'site',
    )


@admin.register(Song)
class SongAdmin(admin.ModelAdmin):

    list_display = (
        '__str__',
        'play_count',
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            _setlist_count=Count("setlists", distinct=True),
        )
        return queryset

    def play_count(self, obj):
        return obj._setlist_count
    play_count.admin_order_field = '_setlist_count'
