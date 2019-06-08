from django.conf import settings
from django.db.utils import IntegrityError

import dropbox
from dateutil import parser as date_parser
from dateutil import relativedelta
from lxml import etree

from reflectsongs.models import Setlist, Song

EXCLUDE = ()
EXCLUDE_LOWER = [x.lower() for x in EXCLUDE]


class ProPresenterImporter(object):
    """Imports playlists and songs from ProPresenter"""

    def get_playlists_from_dropbox(self, site):
        dbx = dropbox.Dropbox(settings.DROPBOX_ACCESS_TOKEN)
        playlist_location = (
            f'{settings.DROPBOX_PATH}/{site.name}/'
            '__Playlist_Data/Default.pro6pl'
        )
        meta, response = dbx.files_download(playlist_location)
        playlist_xml = response.content
        playlists = self._get_playlists(playlist_xml)
        return self._process_playlists(playlists, site)

    def get_playlists_from_file(self, site, filename):
        with open(filename) as plfile:
            playlist_xml = plfile.read().encode('utf-8')
        playlists = self._get_playlists(playlist_xml)
        return self._process_playlists(playlists, site)

    def _get_playlists(self, playlist_xml):
        xmlparser = etree.XMLParser(
            ns_clean=True, recover=True, encoding='utf-8')
        tree = etree.fromstring(playlist_xml, parser=xmlparser)

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

    def _process_playlists(self, playlists, site):
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
