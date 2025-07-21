import os
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from urllib.parse import urlparse

import src.image_filter as ifil

class ImageScraper:

    def __init__(self, im_filter: ifil.ImageFilter=None):
        # create an instances of the food image filter extensions
        if im_filter is not None:
            if not isinstance(im_filter, ifil.ImageFilter):
                raise TypeError("Expected an instance of ImageFilter, got {}".format(type(im_filter)))
            self.image_filter = im_filter
        else:
            filter_extensions = [
                ifil.FoodOrNotImageFilter(verbose=False, version="v2"),
                ifil.SimilarFeatVecImageFilter(verbose=False, threshold=0.97),
                ifil.SimilarHashImageFilter(verbose=False, hamming_distance=5),
            ]

            # create an instance of the image filter
            self.image_filter = ifil.ImageFilter(
                filter_extensions=filter_extensions,
                blur_threshold=100.0,
                uniform_tolerance=0.01
            )


    def run(self, url: list=None, output_dir: str=None):
        if not url:
            raise ValueError("No URL provided")

        if output_dir is None:
            output_dir = os.path.join(os.getcwd(), "scraped_images")

        os.makedirs(output_dir, exist_ok=True)

        settings = get_project_settings()
        # Set the output directory for images
        settings.set('IMAGES_STORE', output_dir, priority='cmdline')
        settings.set('LOG_LEVEL', 'ERROR')  # optional

        process = CrawlerProcess(settings)

        for u in url:
            domain = urlparse(u).netloc
            domain_dir = os.path.join(output_dir, domain)
            os.makedirs(domain_dir, exist_ok=True)

            # Start one spider per URL
            process.crawl('image_spider', urls=[u])

        # Will block until all spiders are done
        process.start()

        print("[ImageScraper] All scraping jobs finished, applying image filters...")
        self.image_filter.filter_images(output_dir)
        print("[ImageScraper] Filtering done.")