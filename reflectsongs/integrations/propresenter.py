import logging
import os
from pathlib import Path
from time import sleep

from django.conf import settings
from django.db.utils import IntegrityError
from django.utils import timezone

import dropbox
from dateutil import parser as date_parser
from dateutil import relativedelta
from lxml import etree

from reflectsongs.models import Setlist, Song
from reflectsongs.utils import grab_songselect_video

logger = logging.getLogger()

EXCLUDE = ()
EXCLUDE_LOWER = [x.lower() for x in EXCLUDE]


class ProPresenterPlaylistImporter(object):
    """Imports playlists from ProPresenter"""

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


class ProPresenterSongImporter(object):
    """Imports songs from ProPresenter"""

    def get_songs_from_dir(self, songs_dir, update=True):
        p = Path(songs_dir)
        paths = list(p.glob('*.pro6'))
        total = len(paths)
        for index, pathitem in enumerate(paths):
            print(f'Item {index+1} of {total}')
            # Read the file
            with pathitem.open() as thefile:
                itemdata = thefile.read().encode('utf-8')
            title = pathitem.with_suffix('').name
            self.parse_item(title, itemdata, update=update)

    def _process_dropbox_entries(self, entries):
        return [entry.path_display for entry in entries
                if isinstance(entry, dropbox.files.FileMetadata)]

    def _get_all_dropbox_filepaths_in_folder(self, folderpath):
        """Get all filepaths inside a dropbox folder"""
        all_items = []
        dbx = dropbox.Dropbox(settings.DROPBOX_ACCESS_TOKEN)
        batch = dbx.files_list_folder(folderpath)
        all_items += self._process_dropbox_entries(batch.entries)
        while batch.has_more:
            batch = dbx.files_list_folder_continue(batch.cursor)
            all_items += self._process_dropbox_entries(batch.entries)
        return all_items

    def get_songs_from_dropbox(self, site, update=True):

        songs_dir = (
            f'{settings.DROPBOX_PATH}/{site.name}/'
            '__Documents/Default/'
        )
        song_paths = self._get_all_dropbox_filepaths_in_folder(songs_dir)
        logger.info('Found {len(songs_paths)} Songs')

        dbx = dropbox.Dropbox(settings.DROPBOX_ACCESS_TOKEN)
        total = len(song_paths)
        for index, song_path in enumerate(song_paths):
            print(f'Processing {index+1} of {total}')
            meta, response = dbx.files_download(song_path)
            song_xml = response.content
            basename = os.path.basename(song_path)
            title, _ = os.path.splitext(basename)
            self.parse_item(title, song_xml, update=update)

    def parse_item(self, item_title, item_xml, update=True):
        xmlparser = etree.XMLParser(
            ns_clean=True, recover=True, encoding='utf-8')
        tree = etree.fromstring(item_xml, parser=xmlparser)

        # Check category
        category = tree.attrib.get('category')
        if category != 'Song':
            # Delete if exists and no ccli number
            items_to_delete = Song.objects.filter(
                title=item_title, ccli_number__exact='')
            for item in items_to_delete:
                print('Removing non-song: {}'.format(item))
                item.delete()
            return

        # Create, or get existing by name
        song, _ = Song.objects.get_or_create(
            title=item_title,
        )
        print('Processing: {}'.format(song))
        changed = False
        pause = False

        # Look up CCLI info
        ccli_mapping = {
            'ccli_number': 'CCLISongNumber',
            'authors': 'CCLIAuthor',
            'copyright_year': 'CCLICopyrightYear',
        }

        for fieldname, xmlfieldname in ccli_mapping.items():
            value = tree.attrib.get(xmlfieldname)
            current_value = getattr(song, fieldname)
            if value and value != current_value:
                setattr(song, fieldname, value)
                changed = True

        # Grab video from songselect
        if update and not song.last_sync:
            if song.songselect_url and not song.youtube_url:
                video_url = grab_songselect_video(song.songselect_url)
                if video_url:
                    print(f'Got video for {song}')
                    song.youtube_url = video_url
                song.last_sync = timezone.now()
                changed = True
                pause = True
            elif not song.last_sync:
                song.last_sync = timezone.now()
                changed = True

        if changed:
            song.save()

        if pause:
            # Pause before contacting external sites again
            print('Pausing...')
            sleep(3)
