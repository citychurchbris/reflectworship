from django.core.management.base import BaseCommand

from reflectsongs.integrations import ProPresenterPlaylistImporter
from reflectsongs.models import Site

EXCLUDE = ()
EXCLUDE_LOWER = [x.lower() for x in EXCLUDE]


class Command(BaseCommand):
    help = 'Imports playlists from ProPresenter'

    def add_arguments(self, parser):
        parser.add_argument('site_name')
        parser.add_argument('--playlist_filename')

    def handle(self, *args, **options):
        site = Site.objects.get(name__iexact=options['site_name'])

        playlist_filename = options['playlist_filename']
        importer = ProPresenterPlaylistImporter()

        if playlist_filename:
            playlists = importer.get_playlists_from_file(site, playlist_filename)
        else:
            playlists = importer.get_playlists_from_dropbox(site)

        importer.process_playlists(playlists, site)
