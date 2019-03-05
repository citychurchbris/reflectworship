import sys

from dateutil import parser as date_parser
from dateutil import relativedelta
from lxml import etree

EXCLUDE = (
    'Default Sunday',
    'Welcome Card',
    '#Countdown Timer (Use every week)',
    'Pre-Service Notices Loop',
    'Post-Service Notices Loop ',
)
EXCLUDE_LOWER = [x.lower() for x in EXCLUDE]


def get_playlists(tree):
    data = []
    playlists = tree.xpath('//RVPlaylistNode[@type="3"]')
    playlists = [x for x in playlists
                 if x.attrib['displayName'].lower() not in EXCLUDE_LOWER]
    for pl in playlists:
        songs = pl.xpath('array/RVDocumentCue')
        song_names = [x.attrib['displayName'] for x in songs
                      if x.attrib['displayName'].lower() not in EXCLUDE_LOWER]
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
            'name': pl.attrib['displayName'],
            'songs': song_names,
        })
    data.sort(key=lambda x: x['date'])
    return data


def process_playlists(playlists):
    all_songs = {}
    for playlist in playlists:
        print(playlist['date'], playlist['name'])
        print(', '.join(playlist['songs']))
        print('--')
    return all_songs


if __name__ == '__main__':
    with open(sys.argv[1]) as plfile:
        pldata = plfile.read()

    xml = pldata.encode('utf-8')
    xmlparser = etree.XMLParser(ns_clean=True, recover=True, encoding='utf-8')
    tree = etree.fromstring(xml, parser=xmlparser)

    playlists = get_playlists(tree)
    all_songs = process_playlists(playlists)

    songlist = list(all_songs.items())
    songlist.sort(key=lambda x: x[1], reverse=True)

    for song in songlist:
        print('{}: {}'.format(song[0], song[1]))
