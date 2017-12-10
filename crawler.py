import asyncio
import requests
from requests.compat import urljoin, urlparse
from bs4 import BeautifulSoup
from bs4.element import Comment
import collections
import pickle
import sys

sys.setrecursionlimit(50000)

async def index(url):
    sitemap = requests.get(url)

    # BeautifulStoneSoup to parse the document
    soup = BeautifulSoup(sitemap.content, "html.parser")
	# find all the <url> tags in the document
    urls = soup.findAll('url')

    global_word_locs = collections.defaultdict(list)

    results = []

    for url in urls:
        loc = url.find('loc').string
        future = asyncio.Future()
        results.append(asyncio.ensure_future(analyse(future, loc)))   

    await asyncio.wait(results)

    for result in results:
        url, word_locs = result.result()

        for word in word_locs:
            global_word_locs[word].append({ url: word_locs[word]})
    
    search_dict = dict(global_word_locs)

    with open('search.index', 'wb') as index:
        pickle.dump(search_dict, index)


def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True



async def analyse(future, url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    print("Indexing: {}".format(url))
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)   

    word_locs = collections.defaultdict(list)

    counter = 0
    for text in visible_texts:
        words = text.split()
        for word in words:
            word_locs[word].append(counter)
            counter += 1

    return url, word_locs
