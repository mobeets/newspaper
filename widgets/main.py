import sys
import time
import os.path
import pathlib
from datetime import datetime

# must add these to path to get relative imports working
CUR_DIR = pathlib.Path(__file__).parent.resolve()
sys.path.append(os.path.join(CUR_DIR, 'maze'))
sys.path.append(os.path.join(CUR_DIR, 'sudoku'))
sys.path.append(os.path.join(CUR_DIR, 'numberlink'))
sys.path.append(os.path.join(CUR_DIR, 'scrapers'))

from maze import maze_generator
from sudoku import sudoku_generator, sudoku_mini
from numberlink import numberlink_generator
from scrapers import sports_scores, sports_standings, sports_teaminfo, sports_headlines, weather, comics, pokemon, movies, music

IMG_DIR = os.path.join(CUR_DIR, '..', 'tex', 'images')
DATA_DIR = os.path.join(CUR_DIR, '..', 'tex', 'data')
DEFAULT_PATHS = {'imagedir': IMG_DIR, 'datadir': DATA_DIR}

def pass_or_raise(error, debug):
	if debug:
		raise
	else:
		print("ERROR", type(error).__name__, "–", error)

def run_widgets(paths=DEFAULT_PATHS, cached=True, debug=False):
	## WEATHER
	
	# weather: saves two images
	print('WEATHER')
	try:
		weather.main(outdir=paths['imagedir'], cached=cached)
	except Exception as error:
		pass_or_raise(error, debug)

	## ARTS AND CULTURE

	# movies: writes .tex
	print('MOVIES')
	try:
		movies.main(outdir=paths['datadir'], cached=cached)
	except Exception as error:
		pass_or_raise(error, debug)
	
	# new best albums from Pitchfork (writes .tex)
	print('MUSIC')
	try:
		music.main(outdir=paths['datadir'], cached=cached)
	except Exception as error:
		pass_or_raise(error, debug)

	## SPORTS SECTION
	print('SPORTS HEADLINES')
	# sports headlines from AP News (writes .tex)
	try:
		sports_headlines.main(outdir=paths['datadir'], cached=cached)
	except Exception as error:
		pass_or_raise(error, debug)

	# sports scores/standings: writes .tex
	print('SPORTS SCORES')
	for sport_name in ['NBA', 'NHL']:
		try:
			sports_scores.main(sport_name, outdir=paths['datadir'], cached=cached)
		except Exception as error:
			pass_or_raise(error, debug)
		try:
			sports_standings.main(sport_name, outdir=paths['datadir'], cached=cached)
		except Exception as error:
			pass_or_raise(error, debug)

	# sports team info
	print('SPORTS TEAMS')
	for team_name in ['Dallas Mavericks', 'Boston Bruins']:
		try:
			sports_teaminfo.main(team_name, outdir=paths['datadir'], cached=cached)
		except Exception as error:
			pass_or_raise(error, debug)

	## GAMES AND COMICS
	print('SUDOKU')
	# sudoku: writes. tex
	try:
		modes = list(sudoku_generator.difficulties.keys())
		mode = modes[datetime.now().weekday() % len(modes)]
		sudoku_generator.main(mode=mode, outdir=paths['datadir'])
	except Exception as error:
		pass_or_raise(error, debug)

	# mini sudoku: writes .tex
	print('SUDOKU MINI')
	try:
		sudoku_mini.main(outdir=paths['datadir'])
	except Exception as error:
		pass_or_raise(error, debug)

	# numberlink: writes. tex
	print('NUMBERLINK')
	try:
		numberlink_generator.main(w=9, h=9, outdir=paths['datadir'])
	except Exception as error:
		pass_or_raise(error, debug)

	# maze: saves two images
	print('MAZE')
	try:
		maze_generator.main(outdir=paths['imagedir'])
	except Exception as error:
		pass_or_raise(error, debug)

	# comics: saves images
	print('COMICS')
	for comic_name in ['xkcd', 'calvinandhobbes', 'pearls']:
		try:
			comics.main(comic_name, outdir=paths['imagedir'], cached=cached)
		except Exception as error:
			pass_or_raise(error, debug)
	time.sleep(3) # wait for comics to finish
	
	# new pokemon (writes .tex and saves .png)
	print('POKEMON')
	try:
		pokemon.main(outdir=paths['imagedir'], datadir=paths['datadir'], cached=cached)
	except Exception as error:
		pass_or_raise(error, debug)

if __name__ == '__main__':
	run_widgets(debug=True)
