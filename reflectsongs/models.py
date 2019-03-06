import uuid

from django.db import models


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
        return str(self.date)

    date = models.DateField()
    name = models.CharField(
        max_length=200,
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
