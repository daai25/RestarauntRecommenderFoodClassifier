# src/web_scraper/pipelines.py
import os
import hashlib
import scrapy
from scrapy.pipelines.images import ImagesPipeline

class CustomImagePipeline(ImagesPipeline):
    def file_path(self, request, response=None, info=None, *, item=None):
        return request.url.split("/")[-1]


# class DomainImagePipeline(ImagesPipeline):
#
#     def file_path(self, request, response=None, info=None, *, item=None):
#         """
#         Customize image storage path: output_dir/<domain>/<hash>.jpg
#         """
#         domain = item.get("domain", "unknown")
#         url = request.url.encode('utf-8')
#         hash_name = hashlib.sha1(url).hexdigest()[:10]
#         filename = f"{hash_name}.jpg"
#         return os.path.join(domain, filename)
#
#     def get_media_requests(self, item, info):
#         """
#         Called for each item with image_urls field. Returns Requests for each image.
#         """
#         for image_url in item.get("image_urls", []):
#             yield scrapy.Request(image_url, meta={'item': item})
#
#     def item_completed(self, results, item, info):
#         """
#         Called after all images are downloaded.
#         """
#         item['images'] = [x for ok, x in results if ok]
#         return item
