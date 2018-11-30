import sys

from lxml import etree

EXCLUDE = (
    'Default Sunday',
    'Welcome Card',
    '#Countdown Timer (Use every week)',
    'Pre-Service Notices Loop',
    'Post-Service Notices Loop ',
)

with open(sys.argv[1]) as plfile:
    pldata = plfile.read()

xml = pldata.encode('utf-8')
parser = etree.XMLParser(ns_clean=True, recover=True, encoding='utf-8')
tree = etree.fromstring(xml, parser=parser)

all_songs = {}

docs = tree.xpath('//RVDocumentCue')
for doc in docs:
    if doc.attrib['displayName'] in EXCLUDE:
        continue
    if '/Documents/ProPresenter6/' not in doc.attrib['filePath']:
        continue
    songname = doc.attrib['displayName']
    if songname in all_songs:
        all_songs[songname] += 1
    else:
        all_songs[songname] = 1

songlist = list(all_songs.items())
songlist.sort(key=lambda x: x[1], reverse=True)

for song in songlist:
    print('{}: {}'.format(song[0], song[1]))
