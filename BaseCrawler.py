from multiprocessing import Process, Queue, current_process
from concurrent.futures.thread import ThreadPoolExecutor
from queue import Empty
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup

DEQUE_TIMEOUT = 20
GET_TIMEOUT = 30


class BaseCrawler(Process):
    def __init__(self, urls_to_process, processed_urls, connections, info, domains=None, *args, **kwargs):
        '''
           urls_to_process :  multiprocessing.Queue
           processed_urls : Manager().dict()
        '''
        super().__init__(*args, **kwargs)
        self.urls_to_process = urls_to_process
        self.processed_urls = processed_urls
        self.connections = connections
        self.info = info
        self.domains = domains

    def append_url_to_process(self, url):
        if url not in self.processed_urls:
            domain = urlparse(url).netloc
            if self.domains and domain not in self.domains:
                return

            self.urls_to_process.put(url)

    def append_linked_urls(self, url, html):
        soup = BeautifulSoup(html, 'html.parser')
        links = soup.find_all('a', href=True)
        for link in links:
            path = link.get('href')
            if path.startswith('/'):
                path = urljoin(url, path)
            self.connections.put((url, path))
            self.append_url_to_process(path)

    def parse_data(self, response):
        '''
            Method to extract info from html; can be overridden in sub-class
            Return Type : Iterable
        '''
        return []

    def extract_data(self, url, response):
        data = self.parse_data(response)
        for element in data:
            self.connections.put((url, element))
            self.info[element] = 0 if (element not in self.info) else self.info[element] + 1

    def crawl(self, url):
        try:
            response = requests.get(url, timeout=GET_TIMEOUT)
        except:
            print(f"Failed to process {url}")
            return
        self.append_linked_urls(url, response.text)
        self.extract_data(url, response)

    def run(self):
        worker_name = current_process().name
        print(f'***** Starting run on  {worker_name}')
        with ThreadPoolExecutor() as pool:
            while True:
                try:
                    url = self.urls_to_process.get(timeout=DEQUE_TIMEOUT)
                    if url in self.processed_urls:
                        continue
                    print(f"{worker_name} - Processing url : {url}")
                    self.processed_urls[url] = True
                    pool.submit(self.crawl, url)

                except Empty:
                    print(f"***** {worker_name} Queue is empty")
                    break
                except Exception as e:
                    print(e)
                    continue