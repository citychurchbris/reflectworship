###
# SongSelect integration
# - mostly pinched from openlp :)
###

import logging
import random

from django.conf import settings

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

YOUTUBE_VIDEO_ROOT = 'https://www.youtube.com/watch?v='
USER_AGENTS = [
    # Taken from https://deviceatlas.com/blog/list-of-user-agent-strings
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246',
    'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1',
]
BASE_URL = 'https://songselect.ccli.com'
LOGIN_PAGE = 'https://profile.ccli.com/account/signin?appContext=SongSelect&returnUrl=https%3a%2f%2fsongselect.ccli.com%2f'  # noqa
LOGIN_URL = 'https://profile.ccli.com'
LOGOUT_URL = BASE_URL + '/account/logout'
SEARCH_URL = BASE_URL + '/search/results'


class SongSelect(object):

    session = None

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': random.choice(USER_AGENTS),
        })
        self.login()

    def login(self):
        logger.info('Logging into songselect')
        try:
            login_page = BeautifulSoup(
                self.session.get(LOGIN_PAGE).content,
                'lxml',
            )
        except requests.exceptions.RequestException as error:
            logger.error('Could not login to SongSelect, {error}'.format(
                error=error))
            return False
        token_input = login_page.find(
            'input', attrs={'name': '__RequestVerificationToken'})
        login_data = {
            '__RequestVerificationToken': token_input['value'],
            'emailAddress': settings.SONGSELECT_USERNAME,
            'password': settings.SONGSELECT_PASSWORD,
            'RememberMe': 'false'
        }
        login_form = login_page.find('form')
        if login_form:
            login_url = login_form.attrs['action']
        else:
            login_url = '/Account/SignIn'

        if not login_url.startswith('http'):
            if login_url[0] != '/':
                login_url = '/' + login_url
            login_url = LOGIN_URL + login_url

        response = self.session.post(
            login_url,
            data=login_data
        )
        response.raise_for_status()

    def _grab_video(self, songselect_url):
        response = self.session.get(songselect_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, features='lxml')
        for iframe in soup.find_all('iframe'):
            src = iframe.get('src')
            if src and 'youtube.com/embed/' in src:
                video_id = src.split('embed/')[-1]
                video_url = YOUTUBE_VIDEO_ROOT + video_id
                return video_url

        return None

    def _grab_metadata(self, songselect_url):
        response = self.session.get(songselect_url)
        response.raise_for_status()
        metadata = {}

        soup = BeautifulSoup(response.text, features='lxml')
        for metalist in soup.find_all('ul', class_='song-meta-list'):
            title = metalist.li.get_text().lower().strip()
            parts = metalist.find_all('li')[1:]
            metadata[title] = ', '.join(
                [x.get_text().strip() for x in parts]
            )
        return metadata

    def parse(self, songselect_url):
        video = self._grab_video(songselect_url)
        meta = self._grab_metadata(songselect_url)
        print(meta)
