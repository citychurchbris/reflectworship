from pathlib import Path
from time import sleep

from django.core.management.base import BaseCommand

from lxml import etree

from reflectsongs.models import Song
from reflectsongs.utils import grab_songselect_video


class Command(BaseCommand):
    help = 'Imports playlists from ProPresenter'

    def add_arguments(self, parser):
        parser.add_argument('songs_dir')

    def handle(self, *args, **options):
        songs_dir = options['songs_dir']
        p = Path(songs_dir)
        for pathitem in p.glob('*.pro6'):
            self.parse_item(pathitem)

    def parse_item(self, pathitem):
        # Read the file
        with pathitem.open() as thefile:
            itemdata = thefile.read()

        # Remove the extension
        title = pathitem.with_suffix('').name

        # Parse XML
        xml = itemdata.encode('utf-8')
        xmlparser = etree.XMLParser(
            ns_clean=True, recover=True, encoding='utf-8')
        tree = etree.fromstring(xml, parser=xmlparser)

        # Check category
        category = tree.attrib.get('category')
        if category != 'Song':
            # skip
            return

        # Create, or get existing by name
        song, _ = Song.objects.get_or_create(
            title=title,
        )
        print('Processing: {}'.format(song))
        changed = False

        # Look up CCLI info
        ccli_mapping = {
            'ccli_number': 'CCLISongNumber',
            'authors': 'CCLIAuthor',
            'copyright_year': 'CCLICopyrightYear',
        }

        for fieldname, xmlfieldname in ccli_mapping.items():
            value = tree.attrib.get(xmlfieldname)
            current_value = getattr(song, fieldname, None)
            if value != current_value:
                setattr(song, fieldname, value)
                changed = True

        if changed:
            song.save()
            # Pause before contacting songselect again
            sleep(3)
