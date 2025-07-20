# web_scraper/items.py

import scrapy

class ImageItem(scrapy.Item):
    image_urls = scrapy.Field()
    images = scrapy.Field()
    image_path = scrapy.Field()