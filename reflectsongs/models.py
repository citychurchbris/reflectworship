import uuid

from django.db import models
from django.utils.translation import gettext as _

from reflectsongs.utils import url_to_link

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


class Song(ModelBase):
    """
    A worship song
    """
    def __str__(self):
        return self.title

    title = models.CharField(
        max_length=200,
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
    )

    youtube_url = models.URLField(
        blank=True,
        null=True,
    )

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
