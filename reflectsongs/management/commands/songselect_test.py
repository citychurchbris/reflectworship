from pprint import pprint

from django.conf import settings
from django.core.management.base import BaseCommand

from reflectsongs.integrations.songselect import SongSelectImporter


class Command(BaseCommand):
    help = 'Test the SongSelect import'

    def add_arguments(self, parser):
        parser.add_argument('ccli_number')

    def handle(self, *args, **options):
        ccli_number = options.get('ccli_number')
        importer = SongSelectImporter()
        importer.login(
            username=settings.SONGSELECT_USERNAME,
            password=settings.SONGSELECT_PASSWORD,
        )
        songdata = importer.get_songdata(ccli_number)
        pprint(songdata)
