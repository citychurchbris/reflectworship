from django.core.management.base import BaseCommand

from reflectsongs.integrations import ProPresenterPlaylistImporter
from reflectsongs.models import Site


class Command(BaseCommand):
    help = 'Inspects playlists from ProPresenter'

    def add_arguments(self, parser):
        parser.add_argument('site_name')
        parser.add_argument('playlist_uid')
        parser.add_argument('--playlist_filename')

    def handle(self, *args, **options):
        site = Site.objects.get(name__iexact=options['site_name'])

        playlist_filename = options['playlist_filename']
        importer = ProPresenterPlaylistImporter()

        if playlist_filename:
            playlists = importer.get_playlists_from_file(site, playlist_filename)
        else:
            playlists = importer.get_playlists_from_dropbox(site)

        for playlist in playlists:
            if playlist['uid'] == options['playlist_uid']:
                for key, value in playlist.items():
                    print(f"{key}:\t{value}")
