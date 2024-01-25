import os.path
import pathlib
import requests
from bs4 import BeautifulSoup

CUR_DIR = pathlib.Path(__file__).parent.resolve()
CACHE_DIR = os.path.join(CUR_DIR, 'cache')

class Scraper:
	def __init__(self, url, cache_file=None, try_cache=True, cache_dir=CACHE_DIR, update_cache=True):
		self.url = url
		self.try_cache = try_cache
		self.update_cache = update_cache
		self.cache_file = cache_file

		if self.try_cache and not self.cache_file:
			raise Exception("You must provide a cache filename if you want to load from cache.")

		self.cache_dir = cache_dir
		self.cache_path = os.path.join(self.cache_dir, self.cache_file + '.html')

		self.content = self.get_content()
		self.soup = BeautifulSoup(self.content, features="lxml")
	
	def is_cached(self):
		return os.path.exists(self.cache_path)

	def load_cached(self):
		return open(self.cache_path).read()

	def fetch(self):
		session = requests.Session()
		response = session.get(self.url)
		content = response.text
		if self.update_cache:
			with open(self.cache_path, 'w') as f:
				f.write(content)
		return content

	def get_content(self):
		if self.try_cache and self.is_cached():
			return self.load_cached()
		else:
			return self.fetch()

if __name__ == '__main__':
	import sys
	sc = Scraper(sys.argv[1], try_cache=False)
	1/0
