# -*- coding: utf-8 -*-

# Code adapted from OpenLP

##########################################################################
# OpenLP - Open Source Lyrics Projection                                 #
# ---------------------------------------------------------------------- #
# Copyright (c) 2008-2019 OpenLP Developers                              #
# ---------------------------------------------------------------------- #
# This program is free software: you can redistribute it and/or modify   #
# it under the terms of the GNU General Public License as published by   #
# the Free Software Foundation, either version 3 of the License, or      #
# (at your option) any later version.                                    #
#                                                                        #
# This program is distributed in the hope that it will be useful,        #
# but WITHOUT ANY WARRANTY; without even the implied warranty of         #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          #
# GNU General Public License for more details.                           #
#                                                                        #
# You should have received a copy of the GNU General Public License      #
# along with this program.  If not, see <https://www.gnu.org/licenses/>. #
##########################################################################
import logging
import random
import re
from html import unescape
from html.parser import HTMLParser
from http.cookiejar import CookieJar
from urllib.parse import urlencode
from urllib.request import HTTPCookieProcessor, URLError, build_opener

from bs4 import BeautifulSoup, NavigableString

from reflectsongs.models import Theme

USER_AGENTS = [
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/52.0.2743.116 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64; rv:47.0) Gecko/20100101 Firefox/47.0',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:46.0) Gecko/20100101 Firefox/46.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:47.0) Gecko/20100101 Firefox/47.0'
]
BASE_URL = 'https://songselect.ccli.com'
LOGIN_PAGE = 'https://profile.ccli.com/account/signin?appContext=SongSelect&returnUrl='\
    'https%3a%2f%2fsongselect.ccli.com%2f'
LOGIN_URL = 'https://profile.ccli.com'
SONG_URL_BASE = "https://songselect.ccli.com/Songs/{ccli_number}"

logger = logging.getLogger(__name__)


class SongSelectImporter(object):
    """
    """
    def __init__(self):
        """
        Set up the song select importer
        """
        self.html_parser = HTMLParser()
        self.opener = build_opener(HTTPCookieProcessor(CookieJar()))
        self.opener.addheaders = [('User-Agent', random.choice(USER_AGENTS))]

    def login(self, username, password):
        """
        Log the user into SongSelect.
        This method takes a username and password
        points which can be used to give the user some form of feedback.

        :param username: SongSelect username
        :param password: SongSelect password
        :return: subscription level on success, None on failure.
        """
        try:
            login_page = BeautifulSoup(self.opener.open(LOGIN_PAGE).read(), 'lxml')
        except (TypeError, URLError) as error:
            logger.exception(
                'Could not login to SongSelect, {error}'.format(error=error))
            return False
        token_input = login_page.find(
            'input', attrs={'name': '__RequestVerificationToken'})
        data = urlencode({
            '__RequestVerificationToken': token_input['value'],
            'emailAddress': username,
            'password': password,
            'RememberMe': 'false'
        })
        login_form = login_page.find('form')
        if login_form:
            login_url = login_form.attrs['action']
        else:
            login_url = '/Account/SignIn'
        if not login_url.startswith('http'):
            if login_url[0] != '/':
                login_url = '/' + login_url
            login_url = LOGIN_URL + login_url
        try:
            posted_page = BeautifulSoup(
                self.opener.open(login_url, data.encode('utf-8')).read(), 'lxml')
        except (TypeError, URLError) as error:
            logger.exception(
                'Could not login to SongSelect, {error}'.format(error=error))
            return False
        else:
            return posted_page

    def get_songdata(self, ccli_number):
        """
        Get the full song details from SongSelect

        :param ccli_number: The song to find
        :param callback: A callback which can be used to indicate progress
        :return: The updated song dictionary
        """
        song_url = SONG_URL_BASE.format(ccli_number=ccli_number)
        logger.debug(f'Grabbing song from {song_url}')
        songdata = {}
        try:
            song_page = BeautifulSoup(self.opener.open(song_url).read(), 'lxml')
        except (TypeError, URLError) as error:
            logger.exception(
                'Could not get song from SongSelect, {error}'.format(
                    error=error
                ))
            return None
        lyrics_link = song_page.find('a', title='View song lyrics')['href']
        try:
            lyrics_page = BeautifulSoup(
                self.opener.open(BASE_URL + lyrics_link).read(), 'lxml')
        except (TypeError, URLError):
            logger.exception('Could not get lyrics from SongSelect')
            return None
        copyright_elements = []
        theme_elements = []
        copyrights_regex = re.compile(r'\bCopyrights\b')
        themes_regex = re.compile(r'\bThemes\b')
        for ul in song_page.find_all('ul', 'song-meta-list'):
            if ul.find('li', string=copyrights_regex):
                copyright_elements.extend(ul.find_all('li')[1:])
            if ul.find('li', string=themes_regex):
                theme_elements.extend(ul.find_all('li')[1:])

        songdata['copyright'] = '/'.join(
            [unescape(li.string).strip() for li in copyright_elements]
        )
        songdata['topics'] = [unescape(li.string).strip() for li in theme_elements]
        songdata['ccli_number'] = song_page.find(
            'div', 'song-content-data').find('ul').find('li')\
            .find('strong').string.strip()

        songdata['verses'] = []
        verses = lyrics_page.find('div', 'song-viewer lyrics').find_all('p')
        verse_labels = lyrics_page.find('div', 'song-viewer lyrics').find_all('h3')
        for verse, label in zip(verses, verse_labels):
            song_verse = {'label': unescape(label.string).strip(), 'lyrics': ''}
            for v in verse.contents:
                if isinstance(v, NavigableString):
                    song_verse['lyrics'] += unescape(v.string).strip()
                else:
                    song_verse['lyrics'] += '\n'
            song_verse['lyrics'] = song_verse['lyrics'].strip(' \n\r\t')
            songdata['verses'].append(song_verse)
        songdata['lyrics'] = '\n\n'.join([
            v['lyrics'] for v in songdata['verses']
        ])
        return songdata

    def sync_song(self, song):
        songdata = self.get_songdata(song.ccli_number)
        if not songdata:
            logger.warning(f'No song data for {song}')
            return
        for themename in songdata.get('topics', []):
            theme, created = Theme.objects.get_or_create(name=themename)
            if created:
                logger.info(f'Added theme: {theme}')
            song.themes.add(theme)
        copyright_info = songdata.get('copyright')
        if copyright_info:
            song.copyright_info = copyright_info
        lyrics = songdata.get('lyrics')
        if lyrics:
            song.lyrics = lyrics
        song.save()
