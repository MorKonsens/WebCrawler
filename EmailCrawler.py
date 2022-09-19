from BaseCrawler import BaseCrawler
import re

class EmailCrawler(BaseCrawler):
    def __init__(self, urls_to_process, processed_urls, connections, info, *args, **kwargs):
        super().__init__(urls_to_process, processed_urls, connections, info, *args, **kwargs)


    def parse_data(self, response):
        html = response.text
        info = set(re.findall(r'[\w\.-]+@[\w\.-]+', html))
        return info