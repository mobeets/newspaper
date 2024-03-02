import time
import random
from functools import reduce
from board import Board
from solver import Solver
from gen import gen_sudoku

def str_base(val, base, length=None):
    """
    converts val (int, base 10) to new base
    """
    res = ''
    while val > 0:
        res = str(val % base) + res
        val //= base # for getting integer division
    if res:
        return res if length is None else res.zfill(length)
    return '0' if length is None else '0'.zfill(length)

def sample_permutation_index():
    """
    gets the index of a random permutation of a 9x9 sudoku

    where number of 9x9 sudoku transformations:
        - (let a "sit" be a base-6 number)
        - row swaps: 6 row permutations per block = 3 sits 
        - col swaps: 6 col permutations per block = 3 sits 
        - stack swaps: 6 stack permutations = 1 sit
        - band swaps: 6 band permutations = 1 sit
        - so we need 8 sits, where:
            - entry 0: row order, block-row 1
            - entry 1: row order, block-row 2
            - entry 2: row order, block-row 3
            - entry 3: col order, block-col 1
            - entry 4: col order, block-col 2
            - entry 5: col order, block-col 3
            - entry 6: stack order
            - entry 7: band order
    """
    # sample random int between 0 and 6**8-1
    index = random.randint(0, (6**8)-1)
    # write in base-6 with length 8
    return str_base(index, 6, 8)

def permutation_to_swaps(index):
    """
    converts a permutation of 012 into a series of swaps

    0: 012 -> []
    1: 021 -> [(1,2)]
    2: 102 -> [(0,1)]
    3: 210 -> [(0,2)]
    4: 120 -> [(0,1), (1,2)]
    5: 201 -> [(0,1), (0,2)]
    """
    swaps = []
    if index == 0:
        pass
    elif index == 1:
        swaps.append((1,2))
    elif index == 2:
        swaps.append((0,1))
    elif index == 3:
        swaps.append((0,2))
    elif index == 4:
        swaps.append((0,1))
        swaps.append((1,2))
    elif index == 5:
        swaps.append((0,1))
        swaps.append((0,2))
    return swaps

class Generator:
    # constructor for generator, reads in a space delimited
    def __init__(self, starting_file=None):

        if starting_file is not None:
            # opening filled puzzle from file
            with open(starting_file) as f:
                # reducing file to a list of numbers
                numbers = filter(lambda x: x in '123456789', list(reduce(lambda x, y: x + y, f.readlines())))
                numbers = list(map(int, numbers))
        else:
            numbers = gen_sudoku(9)
            numbers = [x for xs in numbers for x in xs] # flatten

        # constructing board
        self.board = Board(numbers)

    def randomize(self):
        """
        select a random permutation of the current puzzle
        """
        self.index = sample_permutation_index()
        self.permute_puzzle_from_index(self.index)

    def permute_puzzle_from_index(self, index):
        """
        convert a puzzle permutation index
        into a series of puzzle permutations
        """
        for i, val in enumerate(index):
            if i == 0: # row order, block-row 0
                fcn = self.board.swap_row
                block_index = 0
            elif i == 1: # row order, block-row 1
                fcn = self.board.swap_row
                block_index = 1
            elif i == 2: # row order, block-row 2
                fcn = self.board.swap_row
                block_index = 2
            elif i == 3: # col order, block-col 0
                fcn = self.board.swap_column
                block_index = 0
            elif i == 4: # col order, block-col 1
                fcn = self.board.swap_column
                block_index = 1
            elif i == 5: # col order, block-col 2
                fcn = self.board.swap_column
                block_index = 2
            elif i == 6: # stack order
                fcn = self.board.swap_stack
                block_index = 0
            elif i == 7: # band order
                fcn = self.board.swap_band
                block_index = 0

            v = int(val) # choice
            swaps = permutation_to_swaps(v) # pieces to swap
            for pieces in swaps:
                fcn(3*block_index + pieces[0], 3*block_index + pieces[1])

    # function randomizes an existing complete puzzle
    def randomize_old(self, iterations):
        # not allowing transformations on a partial puzzle
        if len(self.board.get_used_cells()) == 81:

            # looping through iterations
            for x in range(0, iterations):

                # to get a random column/row
                case = random.randint(0, 3)

                # to get a random band/stack
                block = random.randint(0, 2) * 3

                # in order to select which row and column we shuffle an array of
                # indices and take both elements
                options = list(range(0, 3))
                random.shuffle(options)
                piece1, piece2 = options[0], options[1]

                # pick case according to random to do transformation
                if case == 0:
                    self.board.swap_row(block + piece1, block + piece2)
                elif case == 1:
                    self.board.swap_column(block + piece1, block + piece2)
                elif case == 2:
                    self.board.swap_stack(piece1, piece2)
                elif case == 3:
                    self.board.swap_band(piece1, piece2)
        else:
            raise Exception('Rearranging partial board may compromise uniqueness.')

    # method gets all possible values for a particular cell, if there is only one
    # then we can remove that cell
    def reduce_via_logical(self, cutoff=81):
        cells = self.board.get_used_cells()
        random.shuffle(cells)
        for cell in cells:
            if len(self.board.get_possibles(cell)) == 1:
                cell.value = 0
                cutoff -= 1
            if cutoff == 0:
                break

    # method attempts to remove a cell and checks that solution is still unique
    def reduce_via_random(self, cutoff=81, timelimit=None, num_given=None):
        temp = self.board
        tstart = time.time()
        existing = temp.get_used_cells()

        # sorting used cells by density heuristic, highest to lowest
        new_set = [(x, self.board.get_density(x)) for x in existing]
        elements = [x[0] for x in sorted(new_set, key=lambda x: x[1], reverse=True)]

        # for each cell in sorted list
        for cell in elements:
            if timelimit is not None and time.time() - tstart > timelimit:
                print("Reached time limit")
                break
            if num_given is not None and len(self.board.get_used_cells()) <= num_given:
                break
            original = cell.value

            # get list of other values to try in its place
            complement = [x for x in range(1, 10) if x != original]
            ambiguous = False

            # check each value in list of other possibilities to try
            for x in complement:

                # set cell to value
                cell.value = x

                # create instance of solver
                s = Solver(temp)

                # if solver can fill every box and the solution is valid then
                # puzzle becomes ambiguous after removing particular cell, so we can break out
                if s.solve() and s.is_valid():
                    cell.value = original
                    ambiguous = True
                    break

            # if every value was checked and puzzle remains unique, we can remove it
            if not ambiguous:
                cell.value = 0
                cutoff -= 1

            # if we ever meet the cutoff limit we can break out
            if cutoff == 0:
                break

    # returns current state of generator including number of empty cells and a representation
    # of the puzzle
    def get_current_state(self):
        template = "There are currently %d starting cells.\n\rCurrent puzzle state:\n\r\n\r%s\n\r"
        return template % (len(self.board.get_used_cells()), self.board.__str__())
