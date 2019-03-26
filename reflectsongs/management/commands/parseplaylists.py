from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError

from dateutil import parser as date_parser
from dateutil import relativedelta
from lxml import etree

from reflectsongs.models import Setlist, Site, Song

EXCLUDE = (
    'Default Sunday',
    'Welcome Card',
    '#Countdown Timer (Use every week)',
    'Pre-Service Notices Loop',
    'Post-Service Notices Loop ',
)
EXCLUDE_LOWER = [x.lower() for x in EXCLUDE]


class Command(BaseCommand):
    help = 'Imports playlists from ProPresenter'

    def add_arguments(self, parser):
        parser.add_argument('playlist_filename')
        parser.add_argument('site_name')

    def handle(self, *args, **options):
        site = Site.objects.get(name__iexact=options['site_name'])

        with open(options['playlist_filename']) as plfile:
            pldata = plfile.read()

        xml = pldata.encode('utf-8')
        xmlparser = etree.XMLParser(
            ns_clean=True, recover=True, encoding='utf-8')
        tree = etree.fromstring(xml, parser=xmlparser)

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
