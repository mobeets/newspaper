import sys
import os.path
import pathlib
import pandas as pd
from datetime import datetime, timedelta
from pylatexenc.latexencode import unicode_to_latex

# add parent dir so we can import Scraper
CUR_DIR = pathlib.Path(__file__).parent.resolve()
sys.path.append(os.path.abspath(os.path.join(CUR_DIR, '..')))
from base import Scraper

CACHE_DIR = os.path.abspath(os.path.join(CUR_DIR, '..', 'cache'))

BASE_URLS = {
	'NBA': 'https://www.basketball-reference.com/boxscores',
	'NHL': 'https://www.hockey-reference.com/boxscores'
	}

class Standings(Scraper):
	def get(self):
		confs = self.soup.select('.stats_table')
		standings = {}
		for conf in confs:
			conf_name = conf.find('th').text
			teams = conf.select('.full_table')
			standings[conf_name] = []
			for team in teams:
				name = team.find('a').text.split(' ')[0]
				vals = {'name': name}
				for item in team.find_all('td'):
					keys = [k for k in item.attrs if 'data-' in k]
					key = item.attrs[keys[0]]
					vals[key] = item.text
				standings[conf_name].append(vals)
		return standings

	def render_standings(sport, standings):
		if not standings:
			return ''
		output = ''
		for conf in standings:
			df = pd.DataFrame(standings)
			df.index += 1
			df = df.reset_index()
			output += df.style.to_latex()
			output += '\n\n'
		return """{} standings:\n""" + output

	def render(self, sport, standings, outfile=None):
		if standings:
			df = pd.DataFrame(standings)
			df.index += 1
			df = df.reset_index()
			out = '{} standings:\n'.format(sport) + df.style.to_latex()
		else:
			out = ''
		if outfile is not None:
			with open(outfile, 'w') as f:
				f.write(out)
		else:
			print(out)

def main(sport, cached=True, outdir=CACHE_DIR):
	sc = Standings(url=BASE_URLS[sport], try_cache=cached, cache_file='standings-{}'.format(sport))
	standings = sc.get()
	outfile = os.path.join(outdir, 'standings-{}.tex'.format(sport))
	sc.render(sport, standings, outfile=outfile)

if __name__ == '__main__':
	main(sport='NBA', cached=False)
	main(sport='NHL', cached=False)
