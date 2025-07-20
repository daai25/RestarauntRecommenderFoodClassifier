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
