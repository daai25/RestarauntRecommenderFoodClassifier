# src/web_scraper/pipelines.py
import os
import hashlib
import scrapy
from scrapy.pipelines.images import ImagesPipeline

class CustomImagePipeline(ImagesPipeline):
    def file_path(self, request, response=None, info=None, *, item=None):
        return request.url.split("/")[-1]
