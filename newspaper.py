import sys
import shutil
import os.path
import pathlib
import subprocess
from datetime import datetime

CUR_DIR = pathlib.Path(__file__).parent.resolve()
sys.path.append(os.path.join(CUR_DIR, 'widgets'))
from widgets.main import run_widgets

TEMPLATE_DIR = os.path.join(CUR_DIR, 'tex')
RENDERED_DIR = os.path.join(CUR_DIR, 'rendered')
TEMPLATE_NAME = 'newspaper.tex'

LATEX_PATH = '/Library/TeX/texbin/'

def get_paths():
	today = datetime.now()
	issue_number = (today-datetime(2024,1,23)).days
	dirname = today.strftime('%Y%m%d')
	renderdir = os.path.join(RENDERED_DIR, dirname)
	texpath = os.path.join(renderdir, TEMPLATE_NAME)
	imagedir = os.path.join(renderdir, 'images')
	datadir = os.path.join(renderdir, 'data')
	return {'renderdir': renderdir, 'texpath': texpath, 'imagedir': imagedir, 'datadir': datadir, 'templatedir': TEMPLATE_DIR, 'issue_number': issue_number}

def make_new_folder(paths):
	shutil.copytree(paths['templatedir'], paths['renderdir'], dirs_exist_ok=True)

def render_tex(paths):
	# read tex
	with open(paths['texpath']) as f:
		content = f.read()

	# update issue number
	content = content.replace('\currentissue{1}', '\currentissue{{{}}}'.format(paths['issue_number']))

	# write new tex
	with open(paths['texpath'], 'w') as f:
		f.write(content)

def build_tex(paths):
	subprocess.check_output([LATEX_PATH + 'pdflatex', '-output-directory', paths['renderdir'], paths['texpath']])

def main(cached=True):
	# get paths we will use for today's paper
	paths = get_paths()

	# copy template directory to our new directory
	print("Creating new folder...")
	make_new_folder(paths)

	# run each widget (write images to images/ in new dir)
	print("Running widgets...")
	run_widgets(paths, cached)

	# render newspaper.tex
	print("Rendering tex...")
	render_tex(paths)

	# build newspaper.tex -> newspaper.pdf
	print("Building pdf...")
	build_tex(paths)

if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument('--refresh', action='store_true')
	args = parser.parse_args()
	main(cached=not args.refresh)
