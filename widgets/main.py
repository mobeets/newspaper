from .sports import sports
from .weather import weather
from .maze import maze_generator
from .sudoku import sudoku_generator

def run_widgets(paths, cached=True):
	results = {'sudoku': None, 'NBA': None, 'NHL': None}

	# sports: returns NBA and NHL games and standings
	results['NBA'] = sports.main('NBA', cached=cached)
	results['NHL'] = sports.main('NHL', cached=cached)

	# weather: saves two images (must pass dirname)
	weather.main(outdir=paths['imagedir'], cached=cached)

	# games: returns sudoku; saves maze image
	results['sudoku'] = sudoku_generator.main(mode='medium')
	maze_generator.main(outdir=paths['imagedir'])

	# comics: saves images
	# todo

	return results

def render_tex(results, paths):
	# read tex
	with open(paths['texpath']) as f:
		content = f.read()

	# update issue number
	content = content.replace('\currentissue{1}', '\currentissue{{{}}}'.format(paths['issue_number']))

	# render NBA, NHL

	# render sudoku
	tag_start = '\\begin{sudoku-block}'
	tag_end = '\\end{sudoku-block}'
	pre, post = content.split(tag_start)
	_, post = post.split(tag_end)
	sudoku = tag_start + results['sudoku'] + tag_end
	content = pre + sudoku + post

	# write new tex
	with open(paths['texpath'], 'w') as f:
		f.write(content)
