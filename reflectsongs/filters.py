from django.contrib import admin
from django.utils.translation import ugettext as _

from reflectsongs.models import Site


class SiteSongFilter(admin.SimpleListFilter):
    """
    Allow filtering of songs by site
    """

    title = _('Site')
    parameter_name = 'site'

    def lookups(self, request, model_admin):
        return Site.objects.values_list('id', 'name')

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.filter(setlists__site=value)
