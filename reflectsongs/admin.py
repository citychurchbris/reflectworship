from django import forms
from django.contrib import admin
from django.db.models import Count

from easy_select2 import Select2Multiple

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
