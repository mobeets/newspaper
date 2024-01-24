import sys
import os.path
import pathlib

# must add these to path to get relative imports working
CUR_DIR = pathlib.Path(__file__).parent.resolve()
sys.path.append(os.path.join(CUR_DIR, 'maze'))
sys.path.append(os.path.join(CUR_DIR, 'sudoku'))

from sports import sports
from weather import weather
from comics import comics
from maze import maze_generator
from sudoku import sudoku_generator

CACHE_DIR = os.path.join(CUR_DIR, 'cache')
DEFAULT_PATHS = {'imagedir': CACHE_DIR, 'datadir': CACHE_DIR}

def run_widgets(paths=DEFAULT_PATHS, cached=True):
	# sports: returns NBA and NHL games and standings
	sports.main('NBA', outdir=paths['datadir'], cached=cached)
	sports.main('NHL', outdir=paths['datadir'], cached=cached)

	# weather: saves two images (must pass dirname)
	weather.main(outdir=paths['imagedir'], cached=cached)

	# games: returns sudoku; saves maze image
	sudoku_generator.main(mode='medium', outdir=paths['datadir'])
	maze_generator.main(outdir=paths['imagedir'])

	# comics: saves images
	comics.main('xkcd', outdir=paths['imagedir'], cached=cached)

if __name__ == '__main__':
	run_widgets()
