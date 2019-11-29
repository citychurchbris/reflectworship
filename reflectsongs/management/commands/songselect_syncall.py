from time import sleep
import random

from django.conf import settings
from django.core.management.base import BaseCommand

from reflectsongs.integrations.songselect import SongSelectImporter
from reflectsongs.views import get_top_songs


class Command(BaseCommand):
    help = 'Run full SongSelect import'

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=10)
        parser.add_argument('--months', type=int, default=6)

    def handle(self, *args, **options):
        limit = options.get('limit')
        importer = SongSelectImporter()
        print('Logging in')
        importer.login(
            username=settings.SONGSELECT_USERNAME,
            password=settings.SONGSELECT_PASSWORD,
        )
        songs = get_top_songs(
            months=options.get('months')
        )
        done = 0
        for song in songs.all():
            if not song.ccli_number:
                continue
            if song.lyrics:
                continue
            print(f'Syncing {song}')
            importer.sync_song(song)
            done += 1
            if done > limit:
                break
            sleep(random.randint(1,3))
