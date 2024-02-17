import os.path
import random
import numpy as np

puzzle_1 = [[3, 4, 1, 2], [0, 0, 0, 0], [0, 0, 0, 0], [4, 2, 3, 1]]
puzzle_2 = [[4, 0, 0, 1], [0, 1, 3, 0], [0, 4, 1, 0], [1, 0, 0, 3]]
puzzle_3 = [[0, 0, 0, 0], [2, 3, 4, 1], [3, 4, 1, 2], [0, 0, 0, 0]]
puzzle_4 = [[3, 4, 1, 0], [0, 2, 0, 0], [0, 0, 2, 0], [0, 1, 4, 3]]
puzzle_5 = [[0, 0, 0, 3], [3, 2, 4, 0], [0, 4, 3, 2],
            [2, 0, 0, 0]]
# puzzle_6 = [[0, 2, 4, 0], [1, 0, 0, 3], [4, 0, 0, 2], [0, 1, 3, 0]]
# puzzle_7 = [[0, 4, 2, 0], [2, 0, 0, 0], [0, 0, 0, 3], [0, 3, 1, 0]]
puzzles = [puzzle_1, puzzle_2, puzzle_3, puzzle_4, puzzle_5]

def select_random_puzzle():
    return np.vstack(random.choice(puzzles))

def randomly_permute(puzzle):
    # we can permute rows 0/1, rows 2/3, cols 0/1, cols 2/3
    # this means 2^4 = 16 possible permutations
    # so here we randomly sample one of these
    # (we could also do a few more, but why bother)
    index = format(random.choice(range(16)), '04b')

    # convert this index to the flips we will make
    vec = [int(x)==1 for x in index]
    flips = [i for i,x in enumerate(vec) if x]

    # perform row/col flips
    for flip in flips:
        if flip == 0: # flip rows 0/1
            puzzle[[0,1]] = puzzle[[1,0]]
        elif flip == 1: # flip rows 2/3
            puzzle[[2,3]] = puzzle[[3,2]]
        elif flip == 2: # flip cols 0/1
            puzzle = puzzle.T
            puzzle[[0,1]] = puzzle[[1,0]]
            puzzle = puzzle.T
        elif flip == 3: # flip cols 2/3
            puzzle = puzzle.T
            puzzle[[2,3]] = puzzle[[3,2]]
            puzzle = puzzle.T
        else:
            assert False
    return puzzle

def render(puzzle, outfile):
    template = '\starbattlecell{{{}}}{{{}}}{{{}}}'

    out = []
    for col in range(puzzle.shape[0]):
        for row in range(puzzle.shape[1]):
            val = puzzle[col,row]
            if val > 0:
                out.append(template.format(col+1,row+1, val))
    out = '\n'.join(out)

    if outfile is not None:
        with open(outfile, 'w') as f:
            f.write(out)
    else:
        print(out)

def main(outdir=None):
    puzzle = select_random_puzzle()
    puzzle = randomly_permute(puzzle)

    outfile = os.path.join(outdir, 'sudoku_mini.tex') if outdir is not None else None
    render(puzzle, outfile)

if __name__ == '__main__':
    main()
