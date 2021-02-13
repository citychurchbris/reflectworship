import re

from django.utils.html import format_html
from django.utils.text import slugify

import requests
from bs4 import BeautifulSoup

YOUTUBE_VIDEO_ROOT = 'https://www.youtube.com/watch?v='


def url_to_link(url):
    """
    Convert URL to a html link tag
    """
    return format_html("<a href='{url}'>{url}</a>", url=url)


def yt_url_to_id(url):
    """
    Pull the youtube video id from a youtube url
    """
    return url.split('?v=')[-1]


def yt_embed(url):
    """
    Generated embed code for a youtube video
    """
    ytid = yt_url_to_id(url)
    return format_html(
        '<div class="embed-responsive embed-responsive-16by9">'
        '<iframe width="560" height="315" class="embed-responsive-item" '
        'src="https://www.youtube.com/embed/{ytid}" frameborder="0" '
        'allow="encrypted-media; picture-in-picture" allowfullscreen>'
        '</iframe>'
        '</div>',
        ytid=ytid,
    )


def yt_image(url):
    """
    Get preview image from youtube video
    """
    ytid = yt_url_to_id(url)
    return f'https://img.youtube.com/vi/{ytid}/hqdefault.jpg'


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


def unique_slugify(instance,
                   value,
                   slug_field_name='slug',
                   queryset=None,
                   slug_separator='-'):
    """
    Calculates and stores a unique slug of ``value`` for an instance.

    ``slug_field_name`` should be a string matching the name of the field to
    store the slug in (and the field to check against for uniqueness).

    ``queryset`` usually doesn't need to be explicitly provided - it'll default
    to using the ``.all()`` queryset from the model's default manager.
    """
    slug_field = instance._meta.get_field(slug_field_name)

    slug = getattr(instance, slug_field.attname)
    slug_len = slug_field.max_length

    # Sort out the initial slug, limiting its length if necessary.
    slug = slugify(value)
    if slug_len:
        slug = slug[:slug_len]
    slug = _slug_strip(slug, slug_separator)
    original_slug = slug

    # Create the queryset if one wasn't explicitly provided and exclude the
    # current instance from the queryset.
    if queryset is None:
        queryset = instance.__class__._default_manager.all()
    if instance.pk:
        queryset = queryset.exclude(pk=instance.pk)

    # Find a unique slug. If one matches, at '-2' to the end and try again
    # (then '-3', etc).
    next = 2
    while not slug or queryset.filter(**{slug_field_name: slug}):
        slug = original_slug
        end = '%s%s' % (slug_separator, next)
        if slug_len and len(slug) + len(end) > slug_len:
            slug = slug[:slug_len-len(end)]
            slug = _slug_strip(slug, slug_separator)
        slug = '%s%s' % (slug, end)
        next += 1

    setattr(instance, slug_field.attname, slug)


def _slug_strip(value, separator='-'):
    """
    Cleans up a slug by removing slug separator characters that occur at the
    beginning or end of a slug.

    If an alternate separator is used, it will also replace any instances of
    the default '-' separator with the new separator.
    """
    separator = separator or ''
    if separator == '-' or not separator:
        re_sep = '-'
    else:
        re_sep = '(?:-|%s)' % re.escape(separator)
    # Remove multiple instances and if an alternate separator is provided,
    # replace the default '-' separator.
    if separator != re_sep:
        value = re.sub('%s+' % re_sep, separator, value)
    # Remove separator from the beginning and end of the slug.
    if separator:
        if separator != '-':
            re_sep = re.escape(separator)
        value = re.sub(r'^%s+|%s+$' % (re_sep, re_sep), '', value)
    return value
