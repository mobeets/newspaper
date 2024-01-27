import sys
import os.path
import pathlib

# must add these to path to get relative imports working
CUR_DIR = pathlib.Path(__file__).parent.resolve()
sys.path.append(os.path.join(CUR_DIR, 'maze'))
sys.path.append(os.path.join(CUR_DIR, 'sudoku'))
sys.path.append(os.path.join(CUR_DIR, 'numberlink'))

from sports import sports
from weather import weather
from comics import comics
from news import news, pokemon
from movies import movies
from maze import maze_generator
from sudoku import sudoku_generator
from numberlink import gen as numberlink_generator

CACHE_DIR = os.path.join(CUR_DIR, 'cache')
DEFAULT_PATHS = {'imagedir': CACHE_DIR, 'datadir': CACHE_DIR}

def run_widgets(paths=DEFAULT_PATHS, cached=True):
	# sports: writes .tex
	for sport_name in ['NBA', 'NHL']:
		try:
			sports.main(sport_name, outdir=paths['datadir'], cached=cached)
		except:
			pass

	# weather: saves two images
	try:
		weather.main(outdir=paths['imagedir'], cached=cached)
	except:
		pass

	# sudoku: writes. tex
	try:
		sudoku_generator.main(mode='medium', outdir=paths['datadir'])
	except:
		pass

	# numberlink: writes. tex
	try:
		numberlink_generator.main(w=9, h=9, outdir=paths['datadir'])
	except:
		pass

	# maze: saves two images
	try:
		maze_generator.main(outdir=paths['imagedir'])
	except:
		pass

	# comics: saves images
	for comic_name in ['calvinandhobbes', 'pearls']:
		try:
			comics.main(comic_name, outdir=paths['imagedir'], cached=cached)
		except:
			pass

	# sports headlines from AP News (writes .tex)
	try:
		news.main(name='sports', outdir=paths['datadir'], cached=cached)
	except:
		pass
	
	# new best albums from Pitchfork (writes .tex)
	try:
		news.main(name='music', outdir=paths['datadir'], cached=cached)
	except:
		pass
	
	# new pokemon (writes .tex and saves .png)
	try:
		pokemon.main(outdir=paths['imagedir'], datadir=paths['datadir'], cached=cached)
	except:
		pass

	# movies: writes .tex
	try:
		movies.main(outdir=paths['datadir'], cached=cached)
	except:
		pass

if __name__ == '__main__':
	run_widgets()
