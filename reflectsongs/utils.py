from django.utils.html import format_html

import requests
from bs4 import BeautifulSoup

YOUTUBE_VIDEO_ROOT = 'https://www.youtube.com/watch?v='


def url_to_link(url):
    return format_html("<a href='{url}'>{url}</a>", url=url)


def grab_songselect_video(songselect_url):
    response = requests.get(songselect_url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, features='lxml')
    for iframe in soup.find_all('iframe'):
        src = iframe.get('src')
        if src and 'youtube.com/embed/' in src:
            video_id = src.split('embed/')[-1]
            video_url = YOUTUBE_VIDEO_ROOT + video_id
            return video_url

    return None
