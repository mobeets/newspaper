import sys
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
from sudoku import sudoku_generator
from numberlink import numberlink_generator
from scrapers import sports_scores, sports_standings, sports_teaminfo, sports_headlines, weather, comics, pokemon, movies, music

IMG_DIR = os.path.join(CUR_DIR, '..', 'tex', 'images')
DATA_DIR = os.path.join(CUR_DIR, '..', 'tex', 'data')
DEFAULT_PATHS = {'imagedir': IMG_DIR, 'datadir': DATA_DIR}

def pass_or_raise(debug):
	if debug:
		raise
	else:
		pass

def run_widgets(paths=DEFAULT_PATHS, cached=True, debug=False):
	## WEATHER
	
	# weather: saves two images
	try:
		weather.main(outdir=paths['imagedir'], cached=cached)
	except:
		pass_or_raise(debug)

	## ARTS AND CULTURE

	# movies: writes .tex
	try:
		movies.main(outdir=paths['datadir'], cached=cached)
	except:
		pass_or_raise(debug)
	
	# new best albums from Pitchfork (writes .tex)
	try:
		music.main(outdir=paths['datadir'], cached=cached)
	except:
		pass_or_raise(debug)

	## SPORTS SECTION

	# sports headlines from AP News (writes .tex)
	try:
		sports_headlines.main(outdir=paths['datadir'], cached=cached)
	except:
		pass_or_raise(debug)

	# sports scores/standings: writes .tex
	for sport_name in ['NBA', 'NHL']:
		try:
			sports_scores.main(sport_name, outdir=paths['datadir'], cached=cached)
		except:
			pass_or_raise(debug)
		try:
			sports_standings.main(sport_name, outdir=paths['datadir'], cached=cached)
		except:
			pass_or_raise(debug)

	# sports team info
	for team_name in ['Dallas Mavericks', 'Boston Bruins']:
		try:
			sports_teaminfo.main(team_name, outdir=paths['datadir'], cached=cached)
		except:
			pass_or_raise(debug)

	## GAMES AND COMICS

	# sudoku: writes. tex
	try:
		modes = ['medium']*4 + ['hard']*2 + ['extreme']
		mode = modes[datetime.now().weekday()]
		sudoku_generator.main(mode=mode, outdir=paths['datadir'])
	except:
		pass_or_raise(debug)

	# numberlink: writes. tex
	try:
		numberlink_generator.main(w=9, h=9, outdir=paths['datadir'])
	except:
		pass_or_raise(debug)

	# maze: saves two images
	try:
		maze_generator.main(outdir=paths['imagedir'])
	except:
		pass_or_raise(debug)

	# comics: saves images
	for comic_name in ['xkcd', 'calvinandhobbes', 'pearls']:
		try:
			comics.main(comic_name, outdir=paths['imagedir'], cached=cached)
		except:
			pass_or_raise(debug)
	
	# new pokemon (writes .tex and saves .png)
	try:
		pokemon.main(outdir=paths['imagedir'], datadir=paths['datadir'], cached=cached)
	except:
		pass_or_raise(debug)

if __name__ == '__main__':
	run_widgets(debug=True)
