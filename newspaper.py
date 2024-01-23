import shutil
import os.path
import pathlib
import subprocess
from datetime import datetime
from widgets import sports, weather, sudoku_generator, maze_generator

CURDIR = os.path.abspath(os.path.join(pathlib.Path(__file__).parent.resolve()))
TEMPLATE_DIR = os.path.join(CURDIR, 'tex')
RENDERED_DIR = os.path.join(CURDIR, 'rendered')
TEMPLATE_NAME = 'newspaper.tex'

def get_paths():
	dirname = datetime.now().strftime('%Y%m%d')
	dirname = os.path.join(RENDERED_DIR, dirname)
	texpath = os.path.join(dirname, TEMPLATE_NAME)
	imagedir = os.path.join(dirname, 'images')
	return {'renderdir': dirname, 'texpath': texpath, 'imagedir': imagedir, 'templatedir': TEMPLATE_DIR}

def make_new_folder(paths):
	shutil.copytree(paths['templatedir'], paths['dirname'], dirs_exist_ok=True)

def run_widgets(paths, cached):
	results = {'sudoku': None, 'NBA': None, 'NHL': None}

	# sports: returns NBA and NHL games and standings
	results['NBA'] = sports.main('NBA', cached=cached)
	results['NHL'] = sports.main('NHL', cached=cached)

	# weather: saves two images (must pass dirname)
	weather.main(paths['imagedir'], cached=cached)

	# games: returns sudoku; saves maze image
	results['sudoku'] = sudoku_generator.sudoku_generator(mode='medium')
	maze_generator.maze_generator(os.path.join(paths['imagedir'], 'maze.png'))

	# comics: saves images
	# todo

	return results

def render_tex(results, paths):
	# render sudoku, NBA, NHL
	# update vol/edition number
	pass

def build_tex(paths):
	subprocess.check_call(['pdflatex', '-halt-on-error', '-output-directory', paths['dirname'], paths['texpath']])

def main(cached=True):
	# get paths we will use for today's paper
	paths = get_paths()

	# copy template directory to our new directory
	make_new_folder(paths)

	# run each widget (write images to images/ in new dir)
	results = run_widgets(paths, cached)

	# render newspaper.tex (e.g., update sudoko)
	render_tex(results, paths)

	# build newspaper.tex -> newspaper.pdf
	build_tex(paths)

if __name__ == '__main__':
	main()
