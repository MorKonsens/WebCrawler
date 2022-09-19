from BaseCrawler import BaseCrawler
from CrawlerManager import CrawlerManager
from EmailCrawler import EmailCrawler
from WebAnalyzer import WebAnalyzer

CRAWLER_SEED = ['https://www.babydoc.co.il/']
#CRAWLER_SEED = ['https://english.tau.ac.il/']
FILENAME = 'connections.txt'


def main():
    crawler = CrawlerManager(EmailCrawler, CRAWLER_SEED, FILENAME)
    crawler.start_crawling()

    analyzer = WebAnalyzer(FILENAME)
    print("--- Top urls per domain:")
    print("--- Using in degree:")
    main_nodes = analyzer.get_top_by_degree(5)
    for node in main_nodes:
        print(node)

    print("\n--- Using PageRank:")
    top_rank = analyzer.get_top_by_pagerank(5)
    for url in top_rank:
        print(url)


if __name__ == '__main__':
    main()
