import crawler
import asyncio
from aiohttp import web
import json
import collections
import pickle

async def build_index(*args, **kwargs):
    await crawler.index("http://localhost:1313/sitemap.xml")

async def read_from_index():
    with open('search.index', 'r') as index:
        print(index)

async def search(request):
    
    search_index = dict()
    
    with open("search.index", 'rb') as index:
        search_index = pickle.load(index) 

    queries = request.query
    print(queries['q'])
    query = queries['q']

    print(search_index[query])
    response_obj = { 'status': 'success', 'results': search_index[query] }
    
    return web.Response(text=json.dumps(response_obj))


async def handle(request):
    response_obj = { 'status' : 'success' }
    return web.Response(text=json.dumps(response_obj))

app = web.Application()
app.on_startup.append(build_index)

app.router.add_get('/', handle)
app.router.add_get('/search', search)

web.run_app(app)
