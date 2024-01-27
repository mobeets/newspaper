import os.path
import pathlib
import json
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from pylatexenc.latexencode import unicode_to_latex

CURDIR = pathlib.Path(__file__).parent.resolve()
CACHE_DIR = os.path.abspath(os.path.join(CURDIR, '..', 'cache'))
CACHE_PATH = os.path.join(CACHE_DIR, 'scores-{}.html')

MAX_SCORES = 3

BASE_URLS = {
	'NBA': {'recent': 'https://www.basketball-reference.com/boxscores/', 'team_info': 'https://www.basketball-reference.com/teams/DAL/2024.html'},
	'NHL': {'recent': 'https://www.hockey-reference.com/boxscores/', 'team_info': 'https://www.hockey-reference.com/teams/BOS/2024.html'}
	}
TEAM_NAMES = {'NBA': 'Dallas Mavericks', 'NHL': 'Boston Bruins'}

TEAM_PREFS = ['Boston', 'Dallas']

def get_score(team, prefix=''):
	name = team.find('a').text
	score = team.find_all('td')[1].text
	return {prefix: name, prefix + 'score': score}

def game_date(soup):
	dtstr = soup.select('.prevnext')[0].find('span').text
	return datetime.strptime(dtstr, '%b %d, %Y')

def game_date_was_last_night(soup):
	dt_game = game_date(soup)
	dt = datetime.today() - timedelta(days=1)
	return dt.year == dt_game.year and dt.month == dt_game.month and dt.day == dt_game.day

def get_scores(soup, max_scores, team_prefs):
	if not game_date_was_last_night(soup):
		return []

	scores = []
	for item in soup.select('.game_summary'):
		row = get_score(item.select('.winner')[0], 'winner')
		row2 = get_score(item.select('.loser')[0], 'loser')
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

def get_team_info(results, team_name):
	soup = BeautifulSoup(results['team_info'], features="lxml")
	
	items = []
	for tag in ['Record', 'Next Game']:
		item = [x for x in soup.find_all('strong') if tag in x.text][0].parent.text.strip()
		out = ' '.join(item.split())
		if 'Record' in out:
			out = out.split('Division')[0]
		items.append(out)
	return {'name': team_name, 'items': items}

def is_cached(name, cache_path=CACHE_PATH):
	return os.path.exists(cache_path.format(name))

def load_cached(sport, cache_path=CACHE_PATH):
	return json.load(open(cache_path.format(sport)))

def fetch(sport, base_urls, cache_path=CACHE_PATH):
	results = {}
	for name, base_url in base_urls.items():
		session = requests.Session()
		response = session.get(base_url)
		content = response.text
		results[name] = content
	json.dump(results, open(cache_path.format(sport), 'w'))
	return results

def render_scores(sport, scores):
	if not scores:
		return ''
	df = pd.DataFrame(scores)
	table = df.to_latex(index=False, header=False)
	return '\\textbf{' + '{} games last night:\n'.format(sport.upper()) + '}' + table

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

def render_team_info(team_info):
	return '\\textbf{' + team_info['name'] + '}' + '\n\n' + '\n\n'.join(team_info['items'])

def render(scores, standings, sport, team_info, outdir):
	fnm = os.path.join(outdir, '{}_scores.tex'.format(sport))
	with open(fnm, 'w') as f:
		out = render_scores(sport, scores)
		if team_info:
			out += '\n' + render_team_info(team_info)
		f.write(out)

	fnm = os.path.join(outdir, '{}_standings.tex'.format(sport))
	with open(fnm, 'w') as f:
		out = render_standings(sport, standings)
		f.write(out)

def main(sport, outdir=CACHE_DIR, cached=True, max_scores=MAX_SCORES, team_prefs=TEAM_PREFS):

	if cached and is_cached(sport):
		results = load_cached(sport)
	else:
		results = fetch(sport, BASE_URLS[sport])

	soup = BeautifulSoup(results['recent'], features="lxml")
	scores = get_scores(soup, max_scores, team_prefs)
	standings = get_standings(soup)
	team_info = get_team_info(results, TEAM_NAMES[sport])
	render(scores, standings, sport, team_info, outdir)

if __name__ == '__main__':
	# main('NBA', cached=True)
	main('NHL', cached=True)
