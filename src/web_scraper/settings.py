# root/src/web_scraper/settings.py
BOT_NAME = 'web_scraper'

SPIDER_MODULES = ['src.web_scraper.spiders']
NEWSPIDER_MODULE = 'src.web_scraper.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

ITEM_PIPELINES = {
    'src.web_scraper.pipelines.CustomImagePipeline': 1,
}

# enable the random delay middleware
DOWNLOADER_MIDDLEWARES = {
    'src.web_scraper.middleware.RandomDelayMiddleware': 543
}

RANDOM_DELAY_MIN = 0.1
RANDOM_DELAY_MAX = 1.0

# # Configure maximum concurrent requests performed by Scrapy
# CONCURRENT_REQUESTS = 32
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# # Configure a delay for requests for the same website
# MEDIA_DOWNLOAD_TIMEOUT = 1
