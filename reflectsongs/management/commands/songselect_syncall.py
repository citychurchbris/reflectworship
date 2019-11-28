from time import sleep

from django.conf import settings
from django.core.management.base import BaseCommand

from reflectsongs.integrations.songselect import SongSelectImporter
from reflectsongs.views import get_top_songs


class Command(BaseCommand):
    help = 'Run full SongSelect import'

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=10)

    def handle(self, *args, **options):
        limit = options.get('limit')
        importer = SongSelectImporter()
        print('Logging in')
        importer.login(
            username=settings.SONGSELECT_USERNAME,
            password=settings.SONGSELECT_PASSWORD,
        )
        songs = get_top_songs().filter(themes__isnull=True)
        for song in songs[:limit]:
            if not song.ccli_number:
                continue
            print(f'Syncing {song}')
            importer.sync_song(song)
            sleep(1)
