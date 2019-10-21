from django.core.management.base import BaseCommand
from django.db.models import Count

from reflectsongs.models import Song


class Command(BaseCommand):
    help = 'Merges duplicates based on CCLI number'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
        )

    def handle(self, *args, **options):
        duplicate_ccli_numbers = Song.objects.values('ccli_number').annotate(
            Count('id')
        ).order_by().filter(
            id__count__gt=1,
            ccli_number__isnull=False
        ).values_list('ccli_number', flat=True)
        for ccli_number in duplicate_ccli_numbers:
            print(f"Duplicate: {ccli_number}")
            self.merge_ccli_number(ccli_number, options['dry_run'])

    def merge_ccli_number(self, ccli_number, dry_run=False):
        songs = Song.objects.filter(ccli_number=ccli_number)
        most_played = songs.annotate(
            setlist_count=Count('setlists')
        ).order_by('-setlist_count').first()
        print(f"Found song: {most_played}")
        if dry_run:
            return

        for other in songs.exclude(id=most_played.id):
            print(f'Removing duplicate: {other}')
            for setlist in other.setlists.all():
                setlist.songs.remove(other)
                setlist.songs.add(most_played)
                setlist.save()
            other.delete()
