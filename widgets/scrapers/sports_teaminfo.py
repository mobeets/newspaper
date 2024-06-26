import sys
import os.path
import pathlib
import pandas as pd
from datetime import datetime, timedelta
from pylatexenc.latexencode import unicode_to_latex
from base import Scraper, CACHE_DIR

BASE_URLS = {
	'Dallas Mavericks': 'https://www.basketball-reference.com/teams/DAL/2024.html',
	'Boston Bruins': 'https://www.hockey-reference.com/teams/BOS/2024.html'
	}

class TeamInfo(Scraper):
	def get(self):
		info = []
		for tag in ['Record', 'Next Game']:
			items = [x for x in self.soup.find_all('strong') if tag in x.text]
			if len(items) > 0:
				item = [x for x in self.soup.find_all('strong') if tag in x.text][0].parent.text.strip()
				out = ' '.join(item.split())
			else:
				out = ''
			if 'Record' in out:
				out = out.split('Division')[0]
			info.append(out)
		return info

	def render(self, team_name, info, outfile=None):
		if info:
			out = '\\textbf{' + team_name + '}' + '\n\n' + '\n\n'.join(info)
		else:
			out = ''
		if outfile is not None:
			with open(outfile, 'w') as f:
				f.write(out)
		else:
			print(out)

def main(team_name, cached=True, outdir=CACHE_DIR):
	fnm = ''.join(team_name.split())
	sc = TeamInfo(url=BASE_URLS[team_name], try_cache=cached, cache_file='teams-{}'.format(fnm))
	info = sc.get()
	outfile = os.path.join(outdir, 'teams-{}.tex'.format(fnm))
	sc.render(team_name, info, outfile=outfile)

if __name__ == '__main__':
	main(team_name='Dallas Mavericks', cached=False)
	main(team_name='Boston Bruins', cached=False)
