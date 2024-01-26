import os.path
import pathlib
import json
import requests
import subprocess
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime

CURDIR = pathlib.Path(__file__).parent.resolve()
CACHE_DIR = os.path.abspath(os.path.join(CURDIR, '..', 'cache'))
CACHE_PATH = os.path.join(CACHE_DIR, 'comic-{}.html')

BASE_URLS = {
	'xkcd': 'https://xkcd.com/',
	'calvinandhobbes': 'https://www.gocomics.com/calvinandhobbes/{dtstr}',
	'pearls': 'https://www.gocomics.com/pearlsbeforeswine/{dtstr}'
	}

def get_comic(soup, name):
	if name == 'xkcd':
		img = soup.select('#comic')[0].select('img')[0]
		url = 'https:' + img.attrs['src']
		caption = img.attrs['title']
		binary = requests.get(url).content
		return {'url': url, 'binary': binary, 'caption': caption}
	elif name in ['pearls', 'calvinandhobbes']:
		img = soup.select('.comic__image')[0].select('picture')[0].select('img')[0]
		url = img.attrs['src']
		binary = requests.get(url).content
		return {'url': url, 'binary': binary, 'ext': '.gif'}
	return {}

def render(item, outfile):
	if not item.get('binary', ''):
		return
	outfile += item.get('ext', '.png')
	with open(outfile, 'wb') as f:
		f.write(item['binary'])
	if item.get('ext', '.gif'):
		subprocess.check_output(['convert', outfile, outfile.replace('.gif', '.png')])

def is_cached(name, cache_path=CACHE_PATH):
	return os.path.exists(cache_path.format(name))

def load_cached(name, cache_path=CACHE_PATH):
	return json.load(open(cache_path.format(name)))

def fetch_comic(name, base_url, cache_path=CACHE_PATH):
	session = requests.Session()
	response = session.get(base_url)
	content = response.text
	json.dump(content, open(cache_path.format(name), 'w'))
	return content

def main(name, outdir=CACHE_DIR, cached=True):
	if cached and is_cached(name):
		content = load_cached(name)
	else:
		comic_url = BASE_URLS[name]
		if '{dtstr}' in comic_url:
			comic_url = comic_url.format(dtstr=datetime.today().strftime('%Y/%m/%d'))
		content = fetch_comic(name, comic_url)
	soup = BeautifulSoup(content, features="lxml")
	item = get_comic(soup, name)
	render(item, os.path.join(outdir, 'comic-' + name))

if __name__ == '__main__':
	main('calvinandhobbes', cached=True)
