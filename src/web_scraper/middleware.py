import time
import random

class RandomDelayMiddleware:
    def __init__(self, min_delay=0.1, max_delay=1.0):
        self.min_delay = min_delay
        self.max_delay = max_delay

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            min_delay=crawler.settings.getfloat('RANDOM_DELAY_MIN', 0.1),
            max_delay=crawler.settings.getfloat('RANDOM_DELAY_MAX', 1.0)
        )

    def process_request(self, request, spider):
        delay = random.uniform(self.min_delay, self.max_delay)
        time.sleep(delay)