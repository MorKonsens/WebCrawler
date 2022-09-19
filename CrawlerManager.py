from multiprocessing import Queue, Manager
import psutil
from queue import Empty

DEQUE_TIMEOUT = 30

class CrawlerManager:
    def __init__(self, cls, seed_urls, connections_file, domains=None, cpus_num=None):
        self.urls_to_process = Queue()
        self.connections = Queue()
        self.manager = Manager()
        self.processed_urls = self.manager.dict()
        self.info = self.manager.dict()
        self.processes = []
        self.cpus_num = cpus_num if cpus_num else psutil.cpu_count(logical=False)
        self.crawler_class = cls
        self.connections_file = connections_file
        self.domains = domains
        self.add_urls(seed_urls)

    def add_urls(self, urls):
        for url in urls:
            self.urls_to_process.put(url)

    def get_info(self):
        return self.info

    def save_connections(self):
        with open(self.connections_file, "w", encoding="utf-8") as f:
            while True:
                try:
                    connection = self.connections.get(timeout=DEQUE_TIMEOUT)
                    line = ' '.join(str(x) for x in connection)
                    f.write(line + '\n')
                except Empty:
                    return

    def start_crawling(self):
        for i in range(self.cpus_num):
            p = self.crawler_class(self.urls_to_process, self.processed_urls, self.connections, self.info, domains=self.domains)
            self.processes.append(p)
            #p.daemon = True
            p.start()

        self.save_connections()
        [p.join() for p in self.processes]