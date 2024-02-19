import time
import random
from functools import reduce
from board import Board
from solver import Solver

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
    number of 9x9 sudoku transformations:
        - row swaps: 3 blocks, 6 row permutations = 3*6=18
        - col swaps: 3 blocks, 6 row permutations = 3*6=18
        - stack swaps: 6 stack permutations = 6
        - band swaps: 6 band permutations = 6
        - so we could do base 6, length 6, where:
            - entry 1: row index
            - entry 2: row order
            - entry 3: col index
            - entry 4: col order
            - entry 5: stack order
            - entry 6: band order
    """
    return str_base(random.choice(range(6**6)), 6, 6)

class Generator:

    # constructor for generator, reads in a space delimited
    def __init__(self, starting_file):

        # opening file
        f = open(starting_file)

        # reducing file to a list of numbers
        numbers = filter(lambda x: x in '123456789', list(reduce(lambda x, y: x + y, f.readlines())))
        numbers = list(map(int, numbers))

        # closing file
        f.close()

        # constructing board
        self.board = Board(numbers)

    # function randomizes an existing complete puzzle
    def randomize(self, iterations):
        """
        number of transformations:
        - row swaps: 3 blocks, 6 row permutations = 3*6=18
        - col swaps: 3 blocks, 6 row permutations = 3*6=18
        - stack swaps: 6 stack permutations = 6
        - band swaps: 6 band permutations = 6
        - total: 18*18*6*6 = 11664
        - or could do base 6, length 6
            - entry 1: row index
            - entry 2: row order
            - entry 3: col index
            - entry 4: col order
            - entry 5: stack order
            - entry 6: band order
        """

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
    def reduce_via_random(self, cutoff=81, timelimit=None):
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
