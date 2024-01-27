import os.path
import pathlib
import json
import requests
import subprocess
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from pylatexenc.latexencode import unicode_to_latex

CUR_DIR = pathlib.Path(__file__).parent.resolve()
CACHE_DIR = os.path.abspath(os.path.join(CUR_DIR, '..', 'cache'))
HISTORY_PATH = os.path.join(CACHE_DIR, 'movies_shown.txt')
CACHE_PATH = os.path.join(CACHE_DIR, 'movie_list.html')

MAX_SUMMARY_LEN = 200

BASE_URL = 'https://www.rottentomatoes.com/browse/movies_at_home/affiliates:amazon_prime,apple_tv_plus,disney_plus,max_us,netflix~sort:newest'
BASE_MOVIE_URL = 'https://www.rottentomatoes.com'

def update_history(new_movie, history_path=HISTORY_PATH):
	movie_list = load_history(history_path)
	movie_list.append(new_movie.get('name', ''))
	with open(history_path, 'w') as f:
		f.write('\n'.join(movie_list))

def load_history(history_path=HISTORY_PATH):
	if not os.path.exists(history_path):
		return []
	return [x.strip() for x in open(history_path).readlines()]

def pick_movie(movie_list):
	prev_movies = load_history()
	for item in movie_list:
		if item.get('name', '') not in prev_movies:
			return item
	return {}

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
		name = item.select('.p--small')[0].text.strip()
		img_url = item.find('rt-img').attrs['src']
		movie_url = BASE_MOVIE_URL + item.find('a').attrs['href']
		movies.append({'name': name, 'img_url': img_url, 'movie_url': movie_url})
	return movies

def add_movie_info(item):
	if not item.get('movie_url', ''):
		return item
	content = fetch(item['movie_url'], save_cache=False)
	soup = BeautifulSoup(content, features="lxml")

	item['meta'] = soup.select('.info')[0].text
	item['summary'] = [x for x in soup.find_all('p') if x.attrs.get('data-qa', '') == 'movie-info-synopsis'][0].text.strip()
	item['director'] = [x for x in soup.select('.info-item-label') if 'Director' in x.text][0].parent.find('a').text.strip()
	item['starring'] = []
	for name in soup.select('.cast-and-crew-item')[:2]:
		item['starring'].append(name.find('p').text.strip())
	return item

def render(item, outfile, max_summary_len=MAX_SUMMARY_LEN):
	if not item:
		return
	with open(outfile, 'w') as f:
		if not item.get('name', ''):
			return
		out = '\\textbf{' + item['name'] + '}'
		if item.get('meta', ''):
			out += ' ({})'.format(unicode_to_latex(item['meta']))
		if item.get('summary', ''):
			summ = item['summary']
			if len(summ) > max_summary_len:
				summ = summ[:max_summary_len] + '...'
			out += ': {}'.format(unicode_to_latex(summ))
		if item.get('director', ''):
			out += ' Directed by ' + unicode_to_latex(item['director']) + '.'
		if item.get('starring', []):
			out += ' Starring ' + unicode_to_latex(', '.join(item['starring'])) + '.'
		f.write(out)

def main(outdir=CACHE_DIR, cached=True):
	if cached and is_cached():
		content = load_cached()
	else:
		content = fetch()
	soup = BeautifulSoup(content, features="lxml")
	movie_list = get_movie_list(soup)
	movie = pick_movie(movie_list)
	movie = add_movie_info(movie)
	if movie:
		render(movie, os.path.join(outdir, 'movie.tex'))
		if not cached:
			update_history(movie)

if __name__ == '__main__':
	main(cached=True)
