import json
import mimetypes
import os
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse
import requests
import scrapy
from bs4 import BeautifulSoup


class RestarauntcontentspiderSpider(scrapy.Spider):
    """
    A Scrapy spider that scrapes HTML content from restaurant websites 
    listed in a the json file that contains restaraunt info, storing their main and subpage content into 
    structured folders by unique element ID
    """
    name = "restarauntContentSpider"

    custom_settings={
        'RETRY_TIMES': 3,
        'RETRY_HTTP_CODES': [500, 502, 503, 504, 408, 429],
        'DOWNLOAD_DELAY': 0.5,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'CONCURRENT_REQUESTS': 50,
    }

    def __init__(self, *args, **kwargs):
        """
        Initializes the spider, sets internal state, loads restaurant data, and builds a mapping from website URLs to element IDs
        """
        super().__init__(*args, **kwargs)
        self.init_self_values()
        data = self.get_restaurant_json()
        self.build_element_id_map(data)
    
    def init_self_values(self):
        """Initializes the state variables for the spider"""
        self.start_urls = []
        self.url_to_element_id = {}
        self.page_counters = {}
        self.visited_links = {}

    def get_restaurant_json(self):
        """
        Loads the restaurant JSON file for restaraunt information

        Returns:
            dict: Parsed JSON object
        """
        project_root = Path(__file__).resolve().parents[4]
        json_path = os.path.join(project_root, 'data_acquisition', 'open_street_map', 'restaurants_filtered.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def build_element_id_map(self, data):
        """
        Parses the JSON data to extract valid website URLs and 
        builds a mapping from each URL to its corresponding element ID

        Args:
            data (dict): Parsed JSON content
        """
        #for element in data: #Use this line
        for element in data.get("elements", []): #get rid of this line
            tags = element.get("tags", {}) #get rid of this line
            website = tags.get("website") #get rid of this line
            #website = element.get("website") #Use this line
            
            #TODO: Instead of only doing this when there is a website, call x-tr4ce's function that gets that url
            if website and website.startswith("http"):
                self.start_urls.append(website)
                self.url_to_element_id[website] = element["id"]

    def start_requests(self):
        """
        Generates initial Scrapy requests for each restaurant URL,
        passing the associated element ID in the request metadata
        """
        for url in self.start_urls:
            element_id = self.url_to_element_id[url]
            self.visited_links[element_id] = set()
            self.page_counters[element_id] = 0
            if os.path.exists(f"scraped-data/{element_id}"):
                continue
            yield scrapy.Request(url=url, callback=self.parse, meta={'element_id': element_id})

    def parse(self, response):
        """
        Parses the HTML response, saves the cleaned content, and 
        initiates crawling of internal links within the same domain

        Args:
            response (scrapy.http.Response): The HTTP response to parse
        """
        if "text/html" not in response.headers.get("Content-Type", b"").decode("utf-8"):
            return
        element_id = response.meta['element_id']
        element_path = f"scraped-data/{element_id}"
        visited = self.visited_links[element_id]
        
        #Create the direcotires for that site
        self.create_directories(element_path)
        self.save_site_content(response, element_path, element_id)
        yield from self.follow_child_links(response, visited, element_id)

    def create_directories(self, element_path):
        """
        Ensures required subdirectories exist for a given element path

        Args:
            element_path (str): Folder path for the element
        """
        os.makedirs(os.path.join(element_path, "text-content"), exist_ok=True)
        os.makedirs(os.path.join(element_path, "images"), exist_ok=True)
        os.makedirs(os.path.join(element_path, "screenshot"), exist_ok=True)

    def sanitize_html(self, html):
        """
        Removes <script> and <style> tags from the HTML and returns the cleaned HTML as a string

        Args:
            html (str): Raw HTML content

        Returns:
            str: Cleaned HTML
        """
        soup = BeautifulSoup(html, features="lxml")
        for s in soup(['script', 'style']):
            s.decompose()
        return str(soup)
    
    def save_site_content(self, response, element_path, element_id):
        """
        Saves the HTML content of a page to disk using an incremented filename

        Args:
            response (scrapy.http.Response): The response from the scraper
            element_path (str): Directory where the file should be stored
            element_id (str or int): Unique ID for the element from OpenStreetMap
        """
        count = self.page_counters[element_id]
        filename = f"{element_id}_{count}.html"
        self.page_counters[element_id] += 1
        filepath = os.path.join(os.path.join(element_path, "text-content"), filename)
        
        html = self.sanitize_html(response.text)

        # Save HTML
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        self.download_images(html, response.url, element_path, element_id)
    
    def follow_child_links(self, response, visited, element_id):
        """
        Follows and recursively scrapes internal links on the same domain,
        excluding login/register/logout paths

        Args:
            response (scrapy.http.Response): The response to extract links from
            visited (set): Set of previously visited URLs for this element
            element_id (str or int): Unique ID for the element from OpenStreetMap
        """
        # Find and follow internal links
        for link in response.css('a::attr(href)').getall():
            absolute_url = urljoin(response.url, link)
            parsed = urlparse(absolute_url)
            # There are some sites that will go to login pages or something to that effect, and we should avoid those
            skip_keywords = ['login', 'logout', 'register', 'returnurl', 'wp-login', 'wp-admin']
            if any(keyword in absolute_url.lower() for keyword in skip_keywords):
                continue
            if parsed.netloc == urlparse(response.url).netloc and absolute_url not in visited:
                self.visited_links[element_id].add(absolute_url)
                yield scrapy.Request(
                    url=absolute_url,
                    callback=self.parse,
                    meta={'element_id': element_id, 'visited': visited}
                )

    def download_images(self, html, base_url, element_path, element_id):
        """
        Parses and downloads all <img> and lazy-loaded images from a given HTML document,
        saving them incrementally as image files in the corresponding element_id's image folder.

        Args:
            html (str): Cleaned HTML content.
            base_url (str): The URL of the current page (used to resolve relative image links).
            element_path (str): Path to the element's directory (e.g., scraped-data/{element_id}).
            element_id (str or int): The unique identifier of the element.
        """
        soup = BeautifulSoup(html, features="lxml")
        img_tags = soup.find_all("img")
        seen_urls = set()

        image_folder = os.path.join(element_path, "images")
        current_count = len(os.listdir(image_folder))

        for img in img_tags:
            src = img.get("src") or img.get("data-src")
            if not src:
                continue

            # Skip base64 encoded images or duplicates
            if src.startswith("data:") or src in seen_urls:
                continue

            seen_urls.add(src)

            # Resolve absolute URL
            image_url = urljoin(base_url, src)

            response = requests.get(image_url, timeout=10)

            # Guess file extension
            content_type = response.headers.get("Content-Type", "")
            extension = mimetypes.guess_extension(content_type.split(";")[0].strip()) or ".jpg"

            # Save image
            image_path = os.path.join(image_folder, f"{current_count}{extension}")
            with open(image_path, "wb") as f:
                f.write(response.content)
            current_count += 1
