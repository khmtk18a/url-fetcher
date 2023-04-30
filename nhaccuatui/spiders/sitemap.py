import re

from scrapy.spiders import SitemapSpider

# We skip album and video from sitemap.
SITEMAP_IGNORE_PATTERN = r'^https:\/\/www\.nhaccuatui\.com\/sitemap/(album|video)\d{1,}\.xml$'

SONG_URL_PATTERN = r'^https:\/\/www\.nhaccuatui\.com\/bai-hat\/[a-zA-Z0-9-_]+\.[a-zA-Z0-9-_]+\.html$'


class NhaccuatuiSpider(SitemapSpider):
    name = "sitemap"
    sitemap_urls = ("https://www.nhaccuatui.com/robots.txt",)

    def sitemap_filter(self, entries):
        for entry in entries:
            url = entry['loc']
            if re.match(SITEMAP_IGNORE_PATTERN, url):
                self.logger.info(f"skip: {url}")
                continue

            if re.match(SONG_URL_PATTERN, url):
                self.logger.info(f'song: {url}')
                continue

            yield entry
