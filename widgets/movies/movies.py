import os.path
import pathlib
import json
import requests
import subprocess
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime

CUR_DIR = pathlib.Path(__file__).parent.resolve()
CACHE_DIR = os.path.abspath(os.path.join(CUR_DIR, '..', 'cache'))
CACHE_PATH = os.path.join(CACHE_DIR, 'movie_list.html')

BASE_URL = 'https://www.rottentomatoes.com/browse/movies_at_home/affiliates:amazon_prime,apple_tv_plus,disney_plus,max_us,netflix~sort:newest'
BASE_MOVIE_URL = 'https://www.rottentomatoes.com'

def is_cached(cache_path=CACHE_PATH):
	return os.path.exists(cache_path)

def load_cached(cache_path=CACHE_PATH):
	return json.load(open(cache_path))

def fetch(base_url=BASE_URL, cache_path=CACHE_PATH, save_cache=True):
	session = requests.Session()
	response = session.get(base_url)
	content = response.text
	if save_cache:
		json.dump(content, open(cache_path, 'w'))
	return content

def get_movie_list(soup):
	movies = []
	items = soup.select('.discovery-tiles__wrap')[0].select('.flex-container')
	for item in items:
		name = item.find('span').text.strip()
		img_url = item.find('rt-img').attrs['src']
		movie_url = BASE_MOVIE_URL + item.find('a').attrs['href']
		movies.append({'name': name, 'img_url': img_url, 'movie_url': movie_url})
	return movies

def add_movie_info(item):
	content = fetch(item['movie_url'], save_cache=False)
	soup = BeautifulSoup(content, features="lxml")

	item['meta'] = soup.select('.info')[0].text
	item['summary'] = [x for x in soup.find_all('p') if x.attrs.get('data-qa', '') == 'movie-info-synopsis'][0].text.strip()
	item['director'] = [x for x in soup.select('.info-item-label') if 'Director' in x.text][0].parent.find('a').text.strip()
	item['starring'] = []
	for name in soup.select('.cast-and-crew-item')[:2]:
		item['starring'].append(name.find('p').text.strip())
	return item

def render(item, outfile):
	with open(outfile, 'w') as f:
		if not item.get('name', ''):
			return
		out = '\\textbf{' + item['name'] + '}'
		if item.get('meta', ''):
			out += ' ({})'.format(item['meta'])
		if item.get('director', ''):
			out += '\n\n' + '\\textit{' + 'Director}: ' + item['director']
		if item.get('starring', []):
			out += '\n\n' + '\\textit{' + 'Starring}: ' + ', '.join(item['starring'])
		if item.get('summary', ''):
			out += '\n\n{}'.format(item['summary'])
		f.write(out)

def main(outdir=CACHE_DIR, cached=True):
	if cached and is_cached():
		content = load_cached()
	else:
		content = fetch()
	soup = BeautifulSoup(content, features="lxml")
	movie_list = get_movie_list(soup)
	movie = add_movie_info(movie_list[0])
	render(movie, os.path.join(outdir, 'movie.tex'))

if __name__ == '__main__':
	main(cached=True)
