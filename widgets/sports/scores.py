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

MAX_SCORES = 3
BASE_URLS = {
	'NBA': 'https://www.basketball-reference.com/',
	'NHL': 'https://www.hockey-reference.com/'
	}
TEAM_PREFS = ['Boston', 'Dallas', 'Pittsburgh']

class BoxScores(Scraper):
	def get_score(self, team, prefix=''):
		name = team.find('a').text
		score = team.find_all('td')[1].text
		return {prefix: name, prefix + 'score': score}

	def get(self, max_scores=MAX_SCORES, team_prefs=TEAM_PREFS):
		scores = []
		for item in self.soup.select('.game_summary'):
			row = self.get_score(item.select('.winner')[0], 'winner')
			row2 = self.get_score(item.select('.loser')[0], 'loser')
			row.update(row2)
			scores.append(row)

		if len(scores) > max_scores:
			# trim scores, but prioritize some teams
			inds = []
			is_match = lambda tmps, tms: any([tmp in tmc for tmc in tms for tmp in tmps])
			for i in range(len(scores)):
				row = scores[i]
				if is_match(team_prefs, [row['winner'], row['loser']]):
					inds.append(i)
			new_inds = inds + [i for i in range(len(scores)) if i not in inds]
			scores = [scores[i] for i in new_inds[:max_scores]]
		return scores

	def render(self, sport, scores, outfile=None):
		if scores:
			df = pd.DataFrame(scores)
			table = df.to_latex(index=False, header=False)
			out = '\\textbf{' + '{} games last night'.format(sport.upper()) + ':}\n' + table
		else:
			out = ''
		
		if outfile is not None:
			with open(outfile, 'w') as f:
				f.write(out)
		else:
			print(out)

def main(sport, cached=True, outdir=CACHE_DIR):
	sc = BoxScores(url=BASE_URLS[sport], try_cache=cached, cache_file='scores-{}'.format(sport))
	scores = sc.get()
	outfile = os.path.join(outdir, 'scores-{}.tex'.format(sport))
	sc.render(sport, scores, outfile=outfile)

if __name__ == '__main__':
	main(sport='NBA', cached=False)
	main(sport='NHL', cached=False)
