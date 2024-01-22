import shutil
import os.path
import pathlib
import subprocess
from datetime import datetime

CURDIR = os.path.abspath(os.path.join(pathlib.Path(__file__).parent.resolve()))
TEMPLATE_DIR = os.path.join(CURDIR, 'tex')
RENDERED_DIR = os.path.join(CURDIR, 'rendered')
TEMPLATE_NAME = 'newspaper.tex'

def get_paths():
	dirname = datetime.now().strftime('%Y%m%d')
	dirname = os.path.join(RENDERED_DIR, dirname)
	texpath = os.path.join(dirname, TEMPLATE_NAME)
	return dirname, texpath

def make_new_folder(dirname):
	shutil.copytree(TEMPLATE_DIR, dirname, dirs_exist_ok=True)
	return dirname

def run_widgets(dirname):
	results = {}
	return results

def render_tex(results, texpath):
	pass

def build_tex(dirname, texpath):
	subprocess.check_call(['pdflatex', '-halt-on-error', '-output-directory', dirname, texpath])

def main():
	# get paths we will use for today's paper
	dirname, texpath = get_paths()

	# copy template directory to our new directory
	dirname = make_new_folder(dirname)

	# run each widget (write images to images/ in new dir)
	results = run_widgets(dirname)

	# render newspaper.tex (e.g., update sudoko)
	render_tex(results, texpath)

	# build newspaper.tex -> newspaper.pdf
	build_tex(dirname, texpath)

if __name__ == '__main__':
	main()