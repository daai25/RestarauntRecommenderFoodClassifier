import scrapy


class RestarauntcontentspiderSpider(scrapy.Spider):
    name = "restarauntContentSpider"
    allowed_domains = ["test"]
    start_urls = ["https://test"]

    def parse(self, response):
        pass
