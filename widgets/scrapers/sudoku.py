import sys
import json
import os.path
from base import Scraper, CACHE_DIR

BASE_URL = 'https://www.nytimes.com/puzzles/sudoku/hard'
MODES = ['easy', 'medium', 'hard']

class Sudoku(Scraper):
	def get(self, difficulty):
		jscript = self.soup.find_all('script')[2].text
		jscript = jscript.replace('window.gameData = ', '')
		obj = json.loads(jscript)
		puzzle = obj[difficulty]['puzzle_data']['puzzle']
		return puzzle

	def render(self, puzzle, outfile=None):
		if puzzle:
			puzzle = [str(x) if x > 0 else ' ' for x in puzzle]
			rows = [puzzle[i: i+9] for i in range(0, len(puzzle), 9)]
			content = '|' + '|.\n|'.join(['|'.join(row) for row in rows]) + '|.'
			out = """\\begin{sudoku-block}""" + content + """\n\\end{sudoku-block}"""
		else:
			out = ''
		if outfile is not None:
			with open(outfile, 'w') as f:
				f.write(out)
		else:
			print(out)

def main(difficulty, cached=True, outdir=CACHE_DIR):
	sc = Sudoku(url=BASE_URL, try_cache=cached, cache_file='sudoku')
	puzzle = sc.get(difficulty)
	outfile = os.path.join(outdir, 'sudoku.tex')
	sc.render(puzzle, outfile=outfile)

if __name__ == '__main__':
	main(difficulty='hard', cached=False)
