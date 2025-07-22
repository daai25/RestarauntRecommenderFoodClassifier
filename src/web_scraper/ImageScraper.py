import os
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from urllib.parse import urlparse

import src.image_filter as im_filter

class ImageScraper:

    def __init__(self, image_filter: im_filter.ImageFilter=None):
        # create an instances of the food image filter extensions
        if image_filter is not None:
            if not isinstance(image_filter, im_filter.ImageFilter):
                raise TypeError("Expected an instance of ImageFilter, got {}".format(type(image_filter)))
            self.image_filter = image_filter
        else:
            filter_extensions = [
                im_filter.FoodOrNotImageFilter(verbose=False, version="v2"),
                im_filter.SimilarFeatVecImageFilter(verbose=False, threshold=0.97),
                im_filter.SimilarHashImageFilter(verbose=False, hamming_distance=5),
            ]

            # create an instance of the image filter
            self.image_filter = im_filter.ImageFilter(
                filter_extensions=filter_extensions,
                blur_threshold=100.0,
                uniform_tolerance=0.01
            )


    def run(self, url: list=None, output_dir: str=None, do_filter: bool=True):
        """
        Run the image scraper to download images from the provided URLs and optionally filter them.

        Args:
            url (list): List of URLs to scrape images from. If None, no scraping will be performed.
            output_dir (str): Directory where the images will be saved. If None, defaults to "scraped_images" in the current working directory.
            do_filter (bool): If True, apply image filters after scraping. Default is True.
        Raises:
            ValueError: If no URL is provided.
            TypeError: If the provided image_filter is not an instance of ImageFilter.
        """
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
            # replace all the special characters in the domain name with underscores
            domain = (domain
                .replace('.', '_')
                .replace('-', '_')
                .replace(':', '_')
            )

            domain_dir = os.path.join(output_dir, domain)
            os.makedirs(domain_dir, exist_ok=True)

            # Start one spider per URL
            process.crawl("image_spider", urls=[u])

        # Will block until all spiders are done
        process.start()

        if do_filter:
            print("[ImageScraper] All scraping jobs finished, applying image filters...")
            self.image_filter.filter_images(output_dir)
            print("[ImageScraper] Filtering done.")