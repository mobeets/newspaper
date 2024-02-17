# coding: utf-8
""" SudokuMaker Class """

import math
import random

class SudokuMaker(object):
    """ SudokuMaker """
    def __init__(self, trgt_num):
        self.__trgt_num = trgt_num
        self.__decision_num = int(math.sqrt(trgt_num))

    def make(self):
        """ make sudoku function
        """
        sudoku_list = self.__make_source()
        sudoku_list = self.__shuffle_block(sudoku_list)
        sudoku_list = self.__shuffle_row_per_block(sudoku_list)
        sudoku_list = self.__switch_row_column(sudoku_list)
        sudoku_list = self.__shuffle_block(sudoku_list)
        sudoku_list = self.__shuffle_row_per_block(sudoku_list)
        return sudoku_list

    def __make_source(self):
        """ Return the source list of sudoku
        """
        init_list = list(range(1, self.__trgt_num + 1))

        random.shuffle(init_list)
        source_list = []
        for i in range(self.__trgt_num):
            init_list.insert(0, init_list.pop())
            source_list.append(init_list[:])
        return source_list

    def __shuffle_block(self, in_list):
        """ Shuffle Block
        """
        tmp_block = []
        for i in range(self.__decision_num):
            start = i * self.__decision_num
            step = start + self.__decision_num
            block = in_list[start:step]
            tmp_block.append(block)
        random.shuffle(tmp_block)
        # format
        ret_list = []
        for var in tmp_block:
            ret_list = ret_list + var
        return ret_list

    def __shuffle_row_per_block(self, in_list):
        """ Shuffle Row per Block
        """
        ret_list = []
        for i in range(self.__decision_num):
            start = i * self.__decision_num
            step = start + self.__decision_num
            block = in_list[start:step]
            random.shuffle(block)
            ret_list = ret_list + block
        return ret_list

    def __switch_row_column(self, in_list):
        """ switch row column
        """
        ret_list = [[r[i] for r in in_list] for i in range(self.__trgt_num)]
        return ret_list

if __name__ == '__main__':
    print(SudokuMaker(4).make())
