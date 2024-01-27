import os.path
import pathlib
import requests
import subprocess
from bs4 import BeautifulSoup

CUR_DIR = pathlib.Path(__file__).parent.resolve()
CACHE_DIR = os.path.join(CUR_DIR, '__cache__')

class Scraper:
	def __init__(self, url, cache_file=None, try_cache=True, cache_dir=CACHE_DIR, update_cache=True):
		self.url = url
		self.try_cache = try_cache
		self.update_cache = update_cache
		self.cache_file = cache_file

		if self.try_cache and not self.cache_file:
			raise Exception("You must provide a cache filename if you want to load from cache.")

		self.cache_dir = cache_dir
		if self.cache_file is not None:
			self.cache_path = os.path.join(self.cache_dir, self.cache_file + '.html')
		else:
			self.cache_path = None

		if self.url is not None:
			self.content = self.get_content()
			self.soup = self.parse(self.content)

	def parse(self, content):
		return BeautifulSoup(content, features="lxml")
	
	def is_cached(self):
		return os.path.exists(self.cache_path)

	def load_cached(self):
		return open(self.cache_path).read()

	def fetch_and_save_image(self, url, outfile, handle_gif=False):
		binary = requests.get(url).content
		with open(outfile, 'wb') as f:
			f.write(binary)
		if handle_gif:
			if not outfile.endswith('.gif'):
				raise Exception("Expected .gif when handle_gif=True")
			print('Converting .gif to .png...')
			subprocess.check_output(['convert', outfile, outfile.replace('.gif', '.png')])
		return binary

	def fetch(self, url=None, cache_path=None):
		session = requests.Session()
		response = session.get(url)
		content = response.text
		if cache_path is not None:
			with open(cache_path, 'w') as f:
				f.write(content)
		return content

	def get_content(self):
		if self.try_cache and self.is_cached():
			return self.load_cached()
		else:
			return self.fetch(url=self.url, cache_path=self.cache_path if self.update_cache else None)

if __name__ == '__main__':
	import sys
	sc = Scraper(sys.argv[1], try_cache=False)
	1/0
