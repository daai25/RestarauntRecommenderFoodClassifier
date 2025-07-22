# web_scraper/spiders/ImageSpider.py
import scrapy
from ..items import ImageItem
from urllib.parse import urljoin

class ImageSpider(scrapy.Spider):
    name = "image_spider"

    def __init__(self, url=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not url:
            raise ValueError("Missing URL argument for ImageSpider")
        self.start_urls = [url]

    def parse(self, response, **kwargs):
        image_urls = response.css("img::attr(src)").getall()
        full_urls = [urljoin(response.url, src) for src in image_urls]
        yield ImageItem(image_urls=full_urls)


# from ..items import ImageItem
# import scrapy
#
# from typing import Any
# from urllib.parse import urljoin, urlparse
#
# class ImageSpider(scrapy.Spider):
#     name = "image_spider"
#
#     custom_settings = {
#         'MAX_DEPTH': 3,
#         'MAX_PAGE_COUNT': 20,
#     }
#
#     def __init__(self, urls: list=None, *args, **kwargs: Any):
#         super().__init__(*args, **kwargs)
#         # set the start URL for the spider
#         self.start_urls = []
#         self._set_start_urls(urls)
#         # dictionary to keep track of the number of pages crawled per URL
#         self.page_count = {url: 0 for url in self.start_urls}
#
#         # domains to ignore
#         self._ignored_domains = {
#             "heartbeat-aarau.ch",
#             "grandcasinobaden.ch",
#             "psi.ch/",
#             "impro.usercontent.one",
#             "bindella.ch",
#             "losteria.net",
#         }
#
#         self.ignored_keywords = {
#             "login",
#             "logout",
#             "register",
#             "signup",
#             "mailto:",
#             "tel:",
#             "javascript:",
#             "returnurl",
#             "wp-login",
#             "wp-admin"
#         }
#
#     def _set_start_urls(self, urls: list):
#         """
#         Sets the start URLs for the spider, filtering out invalid URLs
#         """
#         for url in urls:
#             is_valid = url and url.startswith('http')
#
#             if is_valid:
#                 domain = urlparse(url).netloc.lower()
#                 if any(bad in domain for bad in self._ignored_domains):
#                     is_valid = False
#
#             if is_valid:
#                 self.start_urls.append(url)
#
#     def start_requests(self):
#         """
#         Initiates requests to the start URLs, setting the callback to parse
#         """
#         for url in self.start_urls:
#             yield scrapy.Request(url=url, callback=self.parse)
#
#     def parse(self, response, **kwargs: Any):
#         """
#         Parse the page:
#         - extract image URLs
#         - find and follow child links (with domain + depth control)
#
#         Args:
#             response (scrapy.http.Response): The response object containing the page content.
#             **kwargs (Any): Additional keyword arguments.
#         Returns:
#             None: This method yields items, it does not return anything.
#         """
#         origin_domain = urlparse(response.url).netloc.lower()
#         current_depth = response.meta.get('depth', 0)
#
#         # Check depth limit
#         if current_depth > self.custom_settings.get('MAX_DEPTH', 3):
#             return
#
#         # Stop if max pages for this domain is reached
#         self.page_count[origin_domain] += 1
#         if self.page_count[origin_domain] > self.custom_settings.get('MAX_PAGE_COUNT', 20):
#             return
#
#         # Extract and yield images
#         for img_src in response.css('img::attr(src)').getall():
#             absolute_url = response.urljoin(img_src)
#             domain = urlparse(response.url).netloc
#
#             item = ImageItem()
#             item['image_urls'] = [absolute_url]
#             item['domain'] = domain
#             yield item
#
#         # Follow valid child links
#         for href in response.css('a::attr(href)').getall():
#             absolute_url = urljoin(response.url, href)
#             parsed = urlparse(absolute_url)
#
#             # Filter: http(s), same domain, ignored keywords
#             if parsed.scheme in ('http', 'https') \
#                     and parsed.netloc == origin_domain \
#                     and not any(s in absolute_url.lower() for s in self.ignored_keywords):
#
#                 yield scrapy.Request(
#                     url=absolute_url,
#                     callback=self.parse,
#                     meta = {'depth': current_depth + 1}  # ensure correct depth tracking
#                 )
