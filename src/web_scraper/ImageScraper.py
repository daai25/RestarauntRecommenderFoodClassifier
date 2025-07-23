import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

import src.image_filter as im_filter

class ImageScraper:
    """
    A class to scrape images from given URLs and save them to a specified directory.
    """
    def __init__(self):
        """
        Initializes the ImageScraper with image filters.
        """
        self.filter_extensions = [
            im_filter.FoodOrNotImageFilter(version="v3"),
            im_filter.SimilarHashImageFilter(hamming_distance=5)
        ]

        self.image_filter = im_filter.ImageFilter(self.filter_extensions)


    def scrape_images(self, urls: list[str]=None, base_dir: str=None, do_filtering: bool=True):
        """
        Scrapes images from the provided URLs and saves them to the specified base directory.
        Each URL's images are saved in a subdirectory named after the domain of the URL.

        Args:
            urls (list[str]): List of URLs to scrape images from.
            base_dir (str): Base directory where images will be saved.
            do_filtering (bool): If True, applies image filtering after scraping.
        Raises:
            ValueError: If no URLs are provided or if the base directory is not specified.
            OSError: If there is an issue creating the base directory.
        """

        if urls is None or len(urls) == 0:
            raise ValueError("No URLs provided for scraping.")
        if base_dir is None:
            raise ValueError("Base directory for saving images is not provided.")

        # Create the base directory if it does not exist
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)

        for url in urls:
            domain = urlparse(url).netloc

            image_dir = os.path.join(
                base_dir,
                domain.lower().replace(":", "_")
            )

            os.makedirs(image_dir, exist_ok=True)

            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")

            img_tags = soup.find_all("img")

            for i, img in enumerate(img_tags):
                img_url = img.get("src")
                if not img_url:
                    continue

                full_url = urljoin(url, img_url)

                try:
                    img_data = requests.get(full_url).content
                    image_path = os.path.join(image_dir, f"image_{i+1}.jpg")
                    with open(image_path, "wb") as image:
                        image.write(img_data)
                except Exception as e:
                    print(f"Failed to download image from {full_url}: {e}")
                    continue

        # filter images if do_filtering is True
        if do_filtering:
            self.image_filter.filter_images(
                directory=base_dir,
                delete=True,
            )
