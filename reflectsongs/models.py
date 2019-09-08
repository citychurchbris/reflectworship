import uuid

from django.db import models
from django.urls import reverse
from django.utils import formats, timezone
from django.utils.translation import gettext as _

from dateutil.relativedelta import relativedelta

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
        unique=True,
    )

    slug = models.SlugField(
        null=True
    )

    def recent_setlist(self):
        return self.setlists.first()


class Song(ModelBase):
    """
    A worship song
    """
    class Meta:
        ordering = (
            'title',
        )

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

    featured = models.BooleanField(
        help_text=(
            'Featured songs appear at the top of the homepage'
            '*New song* listings'
            ),
        default=False,
    )

    youtube_url = models.URLField(
        blank=True,
        null=True,
    )

    worshiptogether_url = models.URLField(
        blank=True,
        null=True,
    )

    lyrics = models.TextField(
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
            return self.setlists.order_by('-date').first()

    def last_played_site(self, site):
        setlists = self.setlists.filter(site=site)
        if setlists.count():
            return setlists.order_by('-date').first()

    def recent_setlists(self, months=6, site=None):
        now = timezone.now()
        recent = self.setlists.filter(date__gt=now-relativedelta(months=months))
        if site:
            recent = recent.filter(site=site)
        return recent

    @property
    def first_played(self):
        if self.setlists.count():
            return self.setlists.order_by('-date').last()

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


class ChordResource(ModelBase):
    """ Represents a chord download (sheet music) """

    song = models.ForeignKey(
        Song,
        on_delete=models.CASCADE,
        related_name='downloads',
    )
    resource_type = models.CharField(
        max_length=200,
        choices=(
            ('pdf', 'PDF'),
            ('chordpro', 'ChordPro'),
        ),
    )
    song_key = models.CharField(
        max_length=5,
        null=True,
        blank=True,
        choices=(
            ('aflat', 'Ab'),
            ('a', 'A'),
            ('bflat', 'Bb'),
            ('b', 'B'),
            ('c', 'C'),
            ('csharp', 'C'),
            ('dflat', 'Db'),
            ('d', 'D'),
            ('eflat', 'Eb'),
            ('e', 'E'),
            ('f', 'F'),
            ('fsharp', 'F#'),
            ('gflat', 'Gb'),
            ('g', 'G'),
        ),
    )
    attachment = models.FileField(
        upload_to='chordresources',
    )


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

    @property
    def friendly_name(self):
        date = formats.date_format(self.date, 'DATE_FORMAT')
        return f"{date}: {self.site} ({self.short_name})"

    @property
    def short_name(self):
        short = self.name.replace(self.site.name, '')
        return short.strip()

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
