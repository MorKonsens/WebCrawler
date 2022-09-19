import networkx as nx
from urllib.parse import urlparse
import pandas as pd

class WebAnalyzer:
    def __init__(self, filename):
        self.graph = nx.read_edgelist(filename, create_using=nx.DiGraph, nodetype=str, data=False)

    def get_top_by_degree(self, k, domain=None):
        df = pd.DataFrame(self.graph.in_degree, columns=['url', 'rank'])
        return self.get_top(df, k, domain)

    def get_top_by_pagerank(self, k, domain=None):
        ranks = nx.pagerank(self.graph)
        df = pd.DataFrame(ranks.items(), columns=['url', 'rank'])
        return self.get_top(df, k, domain)

    def get_top(self, df, k, domain=None):
        df['domain'] = df.apply(lambda row: (urlparse(row['url']).netloc), axis=1)
        if domain:
            df = df[df['domain'] == domain]
        top = df.groupby(['domain'])['url', 'rank'].apply(lambda x: x.nlargest(k, columns=['rank']))
        return top['url'].tolist()