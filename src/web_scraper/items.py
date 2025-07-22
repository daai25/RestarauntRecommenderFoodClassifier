# web_scraper/items.py
import scrapy

class ImageItem(scrapy.Item):
    """
    Item class for storing image data scraped from web pages.
    """
    image_urls = scrapy.Field()
    images = scrapy.Field()
    # image_path = scrapy.Field()