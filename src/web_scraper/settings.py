# root/src/web_scraper/settings.py
BOT_NAME = 'web_scraper'

SPIDER_MODULES = ['src.web_scraper.spiders']
NEWSPIDER_MODULE = 'src.web_scraper.spiders'

DEFAULT_REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/114.0.0.0 Safari/537.36'
}

IMAGES_STORE = 'override_this_in_runtime'

ITEM_PIPELINES = {
    'scrapy.pipelines.images.ImagesPipeline': 1,
}

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests performed by Scrapy
CONCURRENT_REQUESTS = 32
CONCURRENT_REQUESTS_PER_DOMAIN = 16
CONCURRENT_REQUESTS_PER_IP = 16

# Configure a delay for requests for the same website
MEDIA_DOWNLOAD_TIMEOUT = 15

# enable the random delay middleware
DOWNLOADER_MIDDLEWARES = {
    'web_scraper.middlewares.RandomDelayMiddleware': 543
}

RANDOM_DELAY_MIN = 0.1
RANDOM_DELAY_MAX = 1.0
