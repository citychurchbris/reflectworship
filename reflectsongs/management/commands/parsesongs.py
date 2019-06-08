from django.core.management.base import BaseCommand

from reflectsongs.integrations import ProPresenterSongImporter
from reflectsongs.models import Site


class Command(BaseCommand):
    help = 'Imports playlists from ProPresenter'

    def add_arguments(self, parser):
        parser.add_argument('site_name')
        parser.add_argument('--songs_dir')
        parser.add_argument(
            '--skip-update',
            action='store_true',
        )

    def handle(self, *args, **options):
        site = Site.objects.get(name__iexact=options['site_name'])
        songs_dir = options['songs_dir']
        update = not options['skip_update']

        importer = ProPresenterSongImporter()
        if songs_dir:
            importer.get_songs_from_dir(songs_dir, update=update)
        else:
            importer.get_songs_from_dropbox(site, update=update)
