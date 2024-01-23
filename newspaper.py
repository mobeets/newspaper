import shutil
import os.path
import pathlib
import subprocess
from datetime import datetime
from widgets.run import run_widgets

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
	shutil.copytree(paths['templatedir'], paths['renderdir'], dirs_exist_ok=True)

def render_tex(results, paths):
	# render sudoku, NBA, NHL
	# update vol/edition number
	pass

def build_tex(paths):
	subprocess.check_call(['pdflatex', '-halt-on-error', '-output-directory', paths['renderdir'], paths['texpath']])

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
	main(cached=True)
