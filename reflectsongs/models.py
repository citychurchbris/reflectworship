import uuid

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext as _

from reflectsongs.utils import unique_slugify, url_to_link, yt_image

SONGSELECT_BASE_URL = 'https://songselect.ccli.com/Songs/'


class ModelBase(models.Model):
    """ Common model config """
    class Meta:
        abstract = True

    # UUIDs as primary key
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False)


class Site(ModelBase):
    """
    A single church site or location
    """
    def __str__(self):
        return self.name

    name = models.CharField(
        max_length=200,
    )

    def recent_setlist(self):
        return self.setlists.first()


class Song(ModelBase):
    """
    A worship song
    """
    def __str__(self):
        return self.title

    title = models.CharField(
        max_length=200,
    )

    slug = models.CharField(
        max_length=200,
        blank=True,
    )

    authors = models.CharField(
        max_length=200,
    )

    copyright_year = models.IntegerField(
        blank=True,
        null=True,
    )

    ccli_number = models.CharField(
        _('CCLI Number'),
        max_length=200,
        blank=True,
        null=True,
    )

    youtube_url = models.URLField(
        blank=True,
        null=True,
    )

    last_sync = models.DateTimeField(
        _('Last Sync'),
        null=True,
        blank=True,
    )

    @property
    def last_played(self):
        if self.setlists.count():
            return self.setlists.order_by('-date').first().date

    @property
    def first_played(self):
        if self.setlists.count():
            return self.setlists.order_by('-date').last().date

    @property
    def songselect_url(self):
        if self.ccli_number:
            return SONGSELECT_BASE_URL + self.ccli_number
        else:
            return ''

    @property
    def songselect_link(self):
        if self.ccli_number:
            return url_to_link(self.songselect_url)
        else:
            return ''
    songselect_link.fget.short_description = _('SongSelect Link')

    @property
    def photo(self):
        if self.youtube_url:
            return yt_image(self.youtube_url)

    def get_absolute_url(self):
        return reverse('song-view', args=(self.slug, ))

    def save(self, **kwargs):
        unique_slugify(self, self.title)
        super().save(**kwargs)


class Setlist(ModelBase):
    """
    A set of songs
    """
    class Meta:
        ordering = ('-date', )
        unique_together = (
            ('date', 'name', 'site', ),
        )

    def __str__(self):
        value = '{}: {}'.format(
            str(self.date),
            self.site,
        )
        if self.name:
            value += ' ({})'.format(self.name)
        return value

    date = models.DateField()
    name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
    )
    site = models.ForeignKey(
        Site,
        on_delete=models.CASCADE,
        related_name='setlists',
    )

    songs = models.ManyToManyField(
        Song,
        related_name='setlists',
    )
