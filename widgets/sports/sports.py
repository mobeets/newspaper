import os.path
import pathlib
import json
import requests
import pandas as pd
from bs4 import BeautifulSoup

CURDIR = pathlib.Path(__file__).parent.resolve()
CACHE_DIR = os.path.abspath(os.path.join(CURDIR, '..', 'cache'))
CACHE_PATH = os.path.join(CACHE_DIR, 'scores-{}.html')

MAX_SCORES = 4
BASE_URLS = {
	'NBA': 'https://www.basketball-reference.com/boxscores/',
	'NHL': 'https://www.hockey-reference.com/boxscores/'
	}

TEAM_PREFS = ['Boston', 'Dallas']

def get_score(team, prefix=''):
	name = team.find('a').text
	score = team.find_all('td')[1].text
	return {prefix: name, prefix + 'score': score}

def get_scores(soup, max_scores, team_prefs):
	scores = []
	for item in soup.select('.game_summary'):
		row = get_score(item.select('.winner')[0], 'winner')
		row2 = get_score(item.select('.loser')[0], 'loser')
		row.update(row2)
		scores.append(row)

	if len(scores) > max_scores:
		# trim scores, but prioritize some teams
		inds = []
		for i in range(len(scores)):
			row = scores[i]
			for tm in team_prefs:
				if tm in [row['winner'], row['loser']]:
					inds.append(i)
		new_inds = inds + [i for i in range(len(scores)) if i not in inds]
		scores = [scores[i] for i in new_inds[:max_scores]]
	return scores

def get_standings(soup):
	confs = soup.select('.stats_table')
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

def load_cached(sport, cache_path=CACHE_PATH):
	return json.load(open(cache_path.format(sport)))

def fetch_scores(sport, base_url, cache_path=CACHE_PATH):
	session = requests.Session()
	response = session.get(base_url)
	content = response.text
	json.dump(content, open(cache_path.format(sport), 'w'))
	return content

def render_scores(sport, scores):
	df = pd.DataFrame(scores)
	table = df.to_latex(index=False, header=False)
	return """{} games last night:\n""".format(sport.upper()) + table

def render_standings(sport, standings):
	output = ''
	for conf in standings:
		df = pd.DataFrame(standings)
		df.index += 1
		df = df.reset_index()
		output += df.style.to_latex()
		output += '\n\n'
	return """{} standings:\n""" + output

def render(scores, standings, sport, outdir):
	fnm = os.path.join(outdir, '{}_scores.tex'.format(sport))
	with open(fnm, 'w') as f:
		f.write(render_scores(sport, scores))

	fnm = os.path.join(outdir, '{}_standings.tex'.format(sport))
	with open(fnm, 'w') as f:
		f.write(render_standings(sport, standings))

def main(sport, outdir=CACHE_DIR, cached=True, max_scores=MAX_SCORES, team_prefs=TEAM_PREFS):

	if cached:
		content = load_cached(sport)
	else:
		content = fetch_scores(sport, BASE_URLS[sport])
	soup = BeautifulSoup(content, features="lxml")
	scores = get_scores(soup, max_scores, team_prefs)
	standings = get_standings(soup)
	render(scores, standings, sport, outdir)

if __name__ == '__main__':
	main('NBA', cached=True)
	main('NHL', cached=True)
