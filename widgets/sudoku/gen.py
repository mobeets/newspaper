# source: https://raw.githubusercontent.com/JVinuelas19/Sudoku-Generator/main/sudoku.py
import os.path
import time
import difflib
import random
import pathlib
PUZZLE_DIR = os.path.join(pathlib.Path(__file__).parent.resolve(), 'puzzles')

#This function calculates the current block in the generation and returns the matching list with the current block
#row and column are the indexs for current row and column, blocks is the list containing all the blocks and size is the sudoku dimension (4, 6 or 9)
def insert_into_block(row, column, blocks, size):
    #9x9 block distribution
    if size == 9:
        if row<3:
            if column<3:
                return blocks[0]
            elif column>=3 and column<6:
                return blocks[1]
            else:
                return blocks[2]
        elif row>=3 and row<6:
            if column<3:
                return blocks[3]
            elif column>=3 and column<6:
                return blocks[4]
            else:
                return blocks[5]
        else:
            if column<3:
                return blocks[6]
            elif column>=3 and column<6:
                return blocks[7]
            else:
                return blocks[8]

    #6x6 block_distribution
    elif size == 6 :
        if row<2:
            if column<3:
                return blocks[0]
            else:
                return blocks[1]
        elif row>=2 and row<4:
            if column<3:
                return blocks[2]
            else:
                return blocks[3]
        else:
            if column<3:
                return blocks[4]
            else:
                return blocks[5]
    #4x4 block distribution    
    elif size == 4 :
        if row<2:
            if column<2:
                return blocks[0]
            if column>=2:
                return blocks[1]
        else:
            if column<2:
                return blocks[2]
            if column>=2:
                return blocks[3]
    else:
        print(f'Error in insert_into_block function: No matching size. Value for size is {size} .')

#Generates a sudoku of 9x9, 6x6 or 4x4 depending on the size value (9, 6 or 4). The print_me parameter prints the generated sudoku if it's True and
#does nothing if it's False.
#The function returns the generated rows (enough to allow sudoku storage and reading).
def gen_sudoku(size, print_me=False):
    rows, columns, blocks = [], [], []
    for i in range(size):
        rows.append([]), columns.append([]), blocks.append([])

    sudoku_reset = True
    while sudoku_reset is True:
        regen = False
        tic = time.time()
        for row in rows:
            reset = False
            row_index = rows.index(row)
            row_reset = True
            while row_reset is True:
                for column in columns:
                    column_index = columns.index(column)
                    block = insert_into_block(row_index, column_index, blocks, size)
                    column_reset = True
                    if size == 9:
                        pool = [1,2,3,4,5,6,7,8,9]
                    elif size == 6:
                        pool = [1,2,3,4,5,6]
                    else:
                        pool = [1,2,3,4]      

                    while(column_reset is True):
                        try:
                            index = random.randint(0, len(pool)-1)
                            if pool[index] in column or pool[index] in row or pool[index] in block:
                                pool.pop(index)             
                            else:
                                number = pool[index]
                                column.append(number)
                                row.append(number)
                                block.append(number)
                                column_reset = False
                        except:
                            
                            if time.time()-tic>0.011:
                                rows.clear(), columns.clear(), blocks.clear()
                                #After the clear we need to reset the lists, otherwise the algoritm will get stuck
                                for i in range(size):
                                    rows.append([]), columns.append([]), blocks.append([])
                                regen = True
                            else:
                                row.clear()
                                for i in range(column_index):
                                    block = insert_into_block (row_index, i, blocks, size)
                                    block.pop(-1)
                                    selected_column = columns[i]
                                    selected_column.pop(-1)
                            reset = True
                            break
                            #sys.exit()
                    if reset is True:
                        break  
                #Boolean values management
                if reset is False:
                    row_reset = False
                    if row_index == size-1:
                        sudoku_reset = False
                elif reset is True and regen is False:
                    reset = False
                else:
                    break
            if regen is True:
                break

    toc = time.time()        
    if print_me is True:
        for row in rows:
            print(' '.join([str(x) for x in row]))
    return rows

#Export a number of sudokus with the selected size to a txt file. Generates different files for 4, 6 and 9 size.
def export_sudokus(number, size, outdir=PUZZLE_DIR):
    for i in range(number):
        fnm = os.path.join(outdir, f'sudokus{size}_{i}.txt')
        with open(fnm, 'w') as f:
            rows = gen_sudoku(size)
            for row in rows:
                f.write(' '.join([str(x) for x in row]) + '\n')

def main(option, size=9, number=4):
    if option == 1:
        rows = gen_sudoku(size, print_me=True)
    elif option == 2:
        export_sudokus(number, size)

if __name__ == "__main__":
    main(option=2)
