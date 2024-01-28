import sys
import os.path
import pathlib
import pandas as pd
from datetime import datetime, timedelta
from pylatexenc.latexencode import unicode_to_latex
from base import Scraper, CACHE_DIR

BASE_URLS = {
	'NBA': 'https://www.basketball-reference.com/boxscores',
	'NHL': 'https://www.hockey-reference.com/boxscores'
	}

class Standings(Scraper):
	def get(self):
		confs = self.soup.select('.stats_table')
		lkp = {'wins': 'W', 'losses': 'L', 'win_loss_pct': '\%', 'gb': 'GB', 'points': 'Pts'}
		standings = {}
		for conf in confs:
			conf_name = conf.find('th').text.strip()
			if conf_name == '':
				conf_name = conf.select('.thead')[0].text.strip()
			teams = conf.select('.full_table')
			standings[conf_name] = []
			for team in teams:
				name = team.find('a').text.strip()#.split(' ')[0]
				vals = {'Team': name}
				for item in team.find_all('td'):
					keys = [k for k in item.attrs if 'data-' in k]
					key = item.attrs[keys[0]]
					if key not in lkp:
						continue
					vals[lkp[key]] = item.text
				standings[conf_name].append(vals)
		return standings

	def render(self, sport, standings, outfile=None):
		if standings:
			out = '\\textbf{' + '{} Standings'.format(sport) + '}\n\n'
			for conf in standings:
				df = pd.DataFrame(standings[conf])
				df.index += 1
				out += '\\textit{' + conf + '}\n'
				out += df.style.to_latex(hrules=False) + '\n\n'
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
	main(sport='NBA', cached=True)
	main(sport='NHL', cached=True)
