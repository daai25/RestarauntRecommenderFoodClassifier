# root/src/web_scraper/settings.py
BOT_NAME = 'web_scraper'

SPIDER_MODULES = ['web_scraper.spiders']
NEWSPIDER_MODULE = 'web_scraper.spiders'

ITEM_PIPELINES = {
    'web_scraper.pipelines.CustomImagePipeline': 1,
}

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# # Configure maximum concurrent requests performed by Scrapy
# CONCURRENT_REQUESTS = 32
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# # Configure a delay for requests for the same website
# MEDIA_DOWNLOAD_TIMEOUT = 1

# enable the random delay middleware
DOWNLOADER_MIDDLEWARES = {
    'web_scraper.middleware.RandomDelayMiddleware': 543
}

RANDOM_DELAY_MIN = 0.1
RANDOM_DELAY_MAX = 1.0
