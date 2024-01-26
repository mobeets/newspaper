# !/usr/bin/python
import sys
import os.path
import pathlib
from generator import Generator
CURDIR = pathlib.Path(__file__).parent.resolve()
CACHE_DIR = os.path.abspath(os.path.join(CURDIR, '..', 'cache'))

# setting difficulties and their cutoffs for each solve method
difficulties = {
    'easy': (35, 0), 
    'medium': (81, 5), 
    'hard': (81, 10), 
    'extreme': (81, 15)
}

def render(content, outfile):
    # header = """Jess's Sudoku\\vspace{0.2cm}\n\n"""
    template = """\\begin{sudoku-block}""" + content + """\n\\end{sudoku-block}"""
    print(outfile)
    with open(outfile, 'w') as f:
        f.write(template)

def main(mode='medium', outdir=CACHE_DIR):
    # getting desired difficulty from command line
    difficulty = difficulties[mode]

    # constructing generator object from puzzle file (space delimited columns, line delimited rows)
    gen = Generator(os.path.join(CURDIR, 'base.txt'))

    # applying 100 random transformations to puzzle
    gen.randomize(100)

    # getting a copy before slots are removed
    initial = gen.board.copy()

    # applying logical reduction with corresponding difficulty cutoff
    gen.reduce_via_logical(difficulty[0])

    # catching zero case
    if difficulty[1] != 0:
        # applying random reduction with corresponding difficulty cutoff
        gen.reduce_via_random(difficulty[1])

    # getting copy after reductions are completed
    final = gen.board.copy()

    # render in format used by sudoku latex package
    content = '|' + str(final).replace('_', ' ').replace('\r\n', '|.\n|') + '|.'
    
    render(content, os.path.join(outdir, 'sudoku.tex'))

if __name__ == '__main__':
    main()
