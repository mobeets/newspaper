import sys
import os.path
import pathlib
import random
import requests
from datetime import datetime, timedelta
from pylatexenc.latexencode import UnicodeToLatexEncoder
from base import Scraper, CACHE_DIR

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
		kind = self.soup.select('.dtm-type')[0].find('a').text.strip()
		evols = [x.text.split('\n')[1].strip() for x in self.soup.select('.evolution-profile')[0].find_all('h3')]
		if len(evols) == 1:
			evols = []
		return {'name': name, 'desc': desc, 'index': self.poke_index, 'img_url': img_url, 'kind': kind, 'evols': evols}

	def render(self, item, outfile):
		u = UnicodeToLatexEncoder(unknown_char_policy='replace')
		out = 'Pokémon of the day:\n\\textbf{' + u.unicode_to_latex(item['name']) + '}' + ' (\#{})'.format(u.unicode_to_latex(item['index'])) + ' [{}].'.format(u.unicode_to_latex(item['kind']))
		out += '\n' + u.unicode_to_latex(item['desc'])
		if len(item['evols']) > 0:
			out += '\nEvolutions: {}'.format(' $\\rightarrow$ '.join(u.unicode_to_latex(x) for x in item['evols']))
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
