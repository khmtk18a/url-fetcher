import re
import xml.etree.ElementTree as ET
import pysolr
import json

from scrapy.spiders import SitemapSpider
from scrapy.http import Response

SITEMAP_SONGS_PATTERN = r'^https:\/\/www\.nhaccuatui\.com\/sitemap/song\d{1,}\.xml$'
NAMESPACE = {"doc": "http://www.sitemaps.org/schemas/sitemap/0.9",
             "image": "http://www.google.com/schemas/sitemap-image/1.1"}
SONG_URL_PATTERN = r'^https:\/\/www\.nhaccuatui\.com\/bai-hat\/[a-zA-Z0-9-_]+\.(?P<id>[a-zA-Z0-9-_]+)\.html$'
IMAGE_ATTRIBUTES = ['image:title', 'image:caption', 'image:loc']


class NhaccuatuiSpider(SitemapSpider):
    name = "sitemap"
    sitemap_urls = ("https://www.nhaccuatui.com/robots.txt",)
    solr: pysolr.Solr

    def start_requests(self):
        self.solr = pysolr.Solr(self.settings.get(
            'SOLR_URL'), always_commit=True)
        return super().start_requests()

    def sitemap_filter(self, entries):
        for entry in entries:
            url = entry['loc']
            if re.match(SITEMAP_SONGS_PATTERN, url):
                yield entry

    def _parse_sitemap(self, response: Response):
        if re.match(SITEMAP_SONGS_PATTERN, response.url):
            xml = ET.fromstring(response.body)
            for url in xml.findall('doc:url', namespaces=NAMESPACE):
                loc: str = url.find(
                    'doc:loc', namespaces=NAMESPACE).text  # type: ignore
                id: str = re.match(
                    SONG_URL_PATTERN, loc).group('id')  # type: ignore
                img_node: ET.Element = url.find(
                    'image:image', namespaces=NAMESPACE)  # type: ignore

                name, artist, thumbnail = [img_node.find(
                    i, namespaces=NAMESPACE).text for i in IMAGE_ATTRIBUTES]  # type: ignore

                doc = {'id': id, 'name': name, 'artist': artist,
                       'thumbnail': thumbnail, 'url': loc}
                doc['_source'] = json.dumps(doc)
                self.solr.add(doc)
            return

        return super()._parse_sitemap(response)
