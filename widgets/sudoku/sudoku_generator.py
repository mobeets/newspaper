# !/usr/bin/python
import sys
import os.path
import pathlib
from generator import Generator
CUR_DIR = pathlib.Path(__file__).parent.resolve()

new_mode = True

if new_mode:
    # number of givens
    difficulties = {
        'simple': 31,
        'easy': 30,
        'medium': 29,
        'tough': 28,
        'hard': 27,
        'difficult': 26,
        'extreme': 25
    }
else:
    difficulties = {
        'simple': (81, 9),
        'easy': (81, 11),
        'medium': (81, 13),
        'tough': (81, 14),
        'hard': (81, 15),
        'difficult': (81, 16),
        'extreme': (81, 0)
    }

def render(content, outfile):
    template = """\\begin{sudoku-block}""" + content + """\n\\end{sudoku-block}"""
    
    if outfile is not None:
        with open(outfile, 'w') as f:
            f.write(template)
    else:
        print(content)

def main(mode='medium', outdir=None, timelimit=20):
    # getting desired difficulty from command line
    difficulty = difficulties[mode]

    # constructing generator object from puzzle file (space delimited columns, line delimited rows)
    gen = Generator(os.path.join(CUR_DIR, 'base.txt'))

    # apply random transformations to puzzle
    gen.randomize()

    # getting a copy before slots are removed
    initial = gen.board.copy()

    # applying logical reduction with corresponding difficulty cutoff
    if new_mode:
        gen.reduce_via_logical(81)
    else:
        gen.reduce_via_logical(difficulty[0])
    
    # applying random reduction with corresponding difficulty cutoff
    if new_mode:
        gen.reduce_via_random(81, timelimit=timelimit, num_given=difficulty)
    else:
        gen.reduce_via_random(difficulty[1], timelimit=timelimit)

    print('Made a', mode, 'sudoku with', len(gen.board.get_used_cells()), 'cells')

    # getting copy after reductions are completed
    final = gen.board.copy()

    # render in format used by sudoku latex package
    content = '|' + str(final).replace('_', ' ').replace('\r\n', '|.\n|') + '|.'
    
    outfile = os.path.join(outdir, 'sudoku.tex') if outdir is not None else None
    render(content, outfile)

if __name__ == '__main__':
    for mode in difficulties:
        main(mode=mode)
