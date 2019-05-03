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
        parser.add_argument(
            '--skip-update',
            action='store_true',
        )

    def handle(self, *args, **options):
        songs_dir = options['songs_dir']
        p = Path(songs_dir)
        paths = list(p.glob('*.pro6'))
        total = len(paths)
        for index, pathitem in enumerate(paths):
            print(f'Item {index+1} of {total}')
            self.parse_item(pathitem, update=not options['skip_update'])

    def parse_item(self, pathitem, update=True):
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
            # Delete if exists and no ccli number
            items_to_delete = Song.objects.filter(
                title=title, ccli_number__exact='')
            for item in items_to_delete:
                print('Removing non-song: {}'.format(item))
                item.delete()
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
            if value:
                setattr(song, fieldname, value)
                changed = True

        # Grab video from songselect
        if update:
            if song.songselect_url and not song.youtube_url:
                video_url = grab_songselect_video(song.songselect_url)
                if video_url:
                    print(f'Got video for {song}')
                    song.youtube_url = video_url
                    changed = True
                # Pause before contacting songselect again
                print('Pausing...')
                sleep(3)

        if changed:
            song.save()
