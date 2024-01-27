import sys
import os.path
import pathlib
import random
import requests
from datetime import datetime, timedelta
from pylatexenc.latexencode import unicode_to_latex

# add parent dir so we can import Scraper
CUR_DIR = pathlib.Path(__file__).parent.resolve()
sys.path.append(os.path.abspath(os.path.join(CUR_DIR, '..')))
from base import Scraper

CACHE_DIR = os.path.abspath(os.path.join(CUR_DIR, '..', 'cache'))
BASE_URL = 'https://www.pokemon.com/us/pokedex/{}'

class Pokedex(Scraper):
	def __init__(self, base_url, *args, **kwargs):
		# shuffle pokemon indices deterministically
		random.seed(666)
		inds = list(range(1025))
		random.shuffle(inds)

		# get today's pokemon index
		day_index = (datetime.today() - datetime(2024,1,27)).days
		self.poke_index = inds[day_index]

		url = BASE_URL.format(self.poke_index)
		super().__init__(url, *args, **kwargs)

	def get(self):
		name = self.soup.select('.pokedex-pokemon-pagination-title')[0].text.strip().split()[0]
		desc = self.soup.select('.version-x')[0].text.strip()
		img_url = self.soup.select('.profile-images')[0].find('img').attrs['src']
		return {'name': name, 'desc': desc, 'index': self.poke_index, 'img_url': img_url}

	def render(self, item, outfile):
		out = '\\textbf{' + unicode_to_latex(item['name']) + '}' + ' (\#{})'.format(unicode_to_latex(item['index']))
		out += '\n\n' + unicode_to_latex(item['desc'])
		with open(outfile, 'w') as f:
			f.write(out)
		return out

def main(cached=True, outdir=CACHE_DIR, datadir=CACHE_DIR):
	sc = Pokedex(BASE_URL, try_cache=cached, cache_file='pokedex')
	outfile = os.path.join(datadir, 'pokedex.tex')
	imgfile = os.path.join(outdir, 'pokedex.png')

	pokemon = sc.get()
	sc.fetch_and_save_image(pokemon['img_url'], imgfile)
	print(sc.render(pokemon, outfile))

if __name__ == '__main__':
	main(cached=True)
