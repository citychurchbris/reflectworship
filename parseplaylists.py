from lxml import etree

with open('Default.pro6pl') as plfile:
    pldata = plfile.read()

xml = pldata.encode('utf-8')
parser = etree.XMLParser(ns_clean=True, recover=True, encoding='utf-8')
tree = etree.fromstring(xml, parser=parser)

all_songs = {}

docs = tree.xpath('//RVDocumentCue')
for doc in docs:
    if '/Documents/ProPresenter6/' not in doc.attrib['filePath']:
        continue
    songname = doc.attrib['displayName']
    if songname in all_songs:
        all_songs[songname] += 1
    else:
        all_songs[songname] = 1
