from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError

import dropbox
from dateutil import parser as date_parser
from dateutil import relativedelta
from lxml import etree

from reflectsongs.models import Setlist, Site, Song

EXCLUDE = ()
EXCLUDE_LOWER = [x.lower() for x in EXCLUDE]


class Command(BaseCommand):
    help = 'Imports playlists from ProPresenter'

    def add_arguments(self, parser):
        parser.add_argument('site_name')
        parser.add_argument('--playlist_filename')

    def _playlist_from_dropbox(self, site_name):
        dbx = dropbox.Dropbox(settings.DROPBOX_ACCESS_TOKEN)
        playlist_location = (
            f'{settings.DROPBOX_PATH}/{site_name}/'
            '__Playlist_Data/Default.pro6pl'
        )
        meta, response = dbx.files_download(playlist_location)
        return response.content

    def _playlist_from_file(self, filename):
        with open(filename) as plfile:
            pldata = plfile.read()
        return pldata.encode('utf-8')

    def handle(self, *args, **options):
        site = Site.objects.get(name__iexact=options['site_name'])

        playlist_filename = options['playlist_filename']
        if playlist_filename:
            pldata = self._playlist_from_file(playlist_filename)
        else:
            pldata = self._playlist_from_dropbox(site.name)

        xmlparser = etree.XMLParser(
            ns_clean=True, recover=True, encoding='utf-8')
        tree = etree.fromstring(pldata, parser=xmlparser)

        playlists = self.get_playlists(tree)
        self.process_playlists(playlists, site)

    def get_playlists(self, tree):
        data = []
        playlists = tree.xpath('//RVPlaylistNode[@type="3"]')
        playlists = [
            x for x in playlists
            if x.attrib['displayName'].lower() not in EXCLUDE_LOWER
        ]

        for pl in playlists:
            songs = pl.xpath('array/RVDocumentCue')
            song_names = [
                x.attrib['displayName'] for x in songs
                if x.attrib['displayName'].lower() not in EXCLUDE_LOWER
            ]
            if len(song_names) < 2:
                # unlikely to be a setlist
                continue

            date = None
            for attr in ('displayName', 'modifiedDate'):
                value = pl.attrib[attr]
                try:
                    date = date_parser.parse(value)
                except ValueError:
                    pass

            sunday = date + relativedelta.relativedelta(
                weekday=relativedelta.SU(-1)
            )
            data.append({
                'date': sunday.date(),
                'name': pl.attrib['displayName'].strip(),
                'songs': song_names,
            })
        data.sort(key=lambda x: x['date'])
        return data

    def process_playlists(self, playlists, site):
        for playlist in playlists:
            try:
                setlist = Setlist.objects.create(
                    site=site,
                    name=playlist['name'],
                    date=playlist['date'],
                )
            except IntegrityError:
                # Already exists - skip
                print('Skipping: {}'.format(playlist['name']))
                continue

            print('Created setlist: {}'.format(setlist))
            for songname in playlist['songs']:
                song, _ = Song.objects.get_or_create(
                    title=songname,
                )
                setlist.songs.add(song)
                print('Added song: {}'.format(song))
