"""
SUDOKU

Fill the squares of a 9x9 board with numbers 1-9, so that no two rows, columns
or 3x3 blocks contain the same number twice.


Copyright 2017 George Boukeas (boukeas@gmail.com)

Licensed under the MIT License:

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

The software is provided "as is", without warranty of any kind, express or
implied, including but not limited to the warranties of merchantablity, fitness
for a particular purpose and noninfringement. In no event shall the authors or
copyright holders be liable for any claim, damages or other liability, whether
in an action of contract, tort or otherwise, arising from, out of or in
connection with the software or the use or other dealings in the software.
"""

import argparse
import searchtoy


# representation of problem-specific state

class sudokuState(searchtoy.State):
    """ Instances of the sudokuState class hold the current state of the
        puzzle's board.

        Attributes (in slots):
            nb_placed: the number of squares filled with a number
            board: a representation of the 9x9 puzzle board
    """
    __slots__ = ('nb_placed', 'board')

    def __init__(self):
        self.nb_placed = 0
        self.board = board()
        for row in range(9):
            for col in range(9):
                self.board[row, col] = set(range(1, 10))

    def __str__(self):
        """ Returns a "nicely printable" string representation of the state.
        """
        separator = 25*'-' + '\n'
        result = ['']
        for row in range(9):
            if row % 3 == 0:
                result.append(separator)
            for col in range(0,9):
                if col % 3 == 0:
                    result.append('|')
                position = self.board[row, col]
                if type(position) is int:
                    result.append(str(position))
                else:
                    result.append('.')
            result.append('|\n')
        result.append(separator)
        return " ".join(result)

    def __hash__(self):
        """ Returns a unique integer computed from the current state.
        """
        return "".join([str(self.board[row, col])
                       if type(self.board[row, col]) is int else "."
                       for row in range(9) for col in range(9)]).__hash__()

    def copy(self):
        """ Returns a new state object that is a copy of self.
        """
        new_object = type(self).empty()
        new_object.nb_placed = self.nb_placed
        new_object.board = self.board.copy()
        return new_object

    @classmethod
    def from_file(cls, filename):
        """ Alternate constructor, returns a new tileState object from a file.

            Arguments:
                filename: name of the file containing the puzzle representation
        """
        new_puzzle = cls()
        ### warning: quick and dirty, absolutely no error checking here...
        with open(filename) as f:
            for row in range(9):
                line = f.readline()
                for col in range(9):
                    if line[col] != ".":
                        number = int(line[col])
                        new_puzzle.place(row, col, number)
        return new_puzzle

    def is_complete(self):
        """ Returns True when the puzzle has been solved, or False otherwise.
        """
        return self.nb_placed == 81

    def affected(self, the_row, the_col):
        """ Yields the positions, i.e. (row, col) pairs, that are affected
            when the square at (the_row, the_col) is filled.

            Essentially, the yielded squares are the ones on the same row, the
            same column, or the same 3x3 block.
        """
        # same row
        for col in skiprange(0, 9, skip=the_col):
            yield the_row, col
        # same column
        for row in skiprange(0, 9, skip=the_row):
            yield row, the_col
        # same block
        block_row = (the_row // 3) * 3
        block_col = (the_col // 3) * 3
        for row in skiprange(block_row, block_row + 3, skip=the_row):
            for col in skiprange(block_col, block_col + 3, skip=the_col):
                yield row, col

    @searchtoy.operator
    def place(self, the_row, the_col, number):
        """ Fills the square at (the_row, the_col) with the number and
            propagates to the affected domains.
        """
        self.nb_placed += 1
        self.board[the_row, the_col] = number
        for row, col in self.affected(the_row, the_col):
            domain = self.board[row, col]
            if type(domain) is set:
                domain.discard(number)


# generation of successor states

class SequentialGenerator(searchtoy.ConsistentGenerator):
    """ Yields the operations that can be performed on a state.

        In this case, the operations are all legal number placements on the
        first available square.
    """
    requires = sudokuState
    graph = False

    @staticmethod
    def selectSquare(state):
        """ Returns the position of the first square on the board not yet filled
            with a number.
        """
        for row in range(9):
            for col in range(9):
                if type(state.board[row, col]) is set:
                    return row, col

    @classmethod
    def operations(cls, state):
        """ Yields the operations that can be performed on a state.

            In this case, operations involve filling a selected square with
            all consistent numbers.
        """
        row, col = cls.selectSquare(state)
        domain = state.board[row, col]
        for number in domain:
            yield state.operators.place(row, col, number)


class MostConstrainedGenerator(SequentialGenerator):
    """ Yields the operations that can be performed on a state.

        In this case, the operations are all legal number placements on the
        most constrained square, i.e. the square with the smallest domain.

        The difference with the SequentialGenerator superclass lies simply
        in the way the next square to be filled is selected.
    """
    requires = sudokuState
    graph = True

    @staticmethod
    def selectSquare(state):
        """ Returns the position of the first square on the board with the
            smallest domain.
        """
        _, position = min((len(state.board[row, col]), (row, col))
                          for row in range(9)
                          for col in range(9)
                          if type(state.board[row, col]) is set)
        return position

# auxillary

class board(dict):
    """ A dict holding the contents of the board. Every (row, col) pair,
        is mapped either to an integer, which means the square has been filled,
        or to its domain, i.e. the set of integers which can legally fill the
        square.
    """

    def __getitem__(self, coords):
        """ Returns the value at coords (which is a row, col pair), or
            None if none exists.
        """
        return self.get(coords)

    def __setitem__(self, coords, value):
        """ Sets the value at coords (which is a row, col pair).
        """
        super().__setitem__(coords, value)

    def copy(self):
        """ Returns a copy of the board.
        """
        new_board = type(self).__new__(type(self))
        for key, value in self.items():
            if type(value) is int:
                new_board[key] = value
            else:
                new_board[key] = value.copy()
        return new_board


def skiprange(start, end, *, skip):
    """ Yields the integers in the ranges [start, skip) and (skip, end).
    """
    for i in range(start, skip):
        yield i
    for i in range(skip + 1, end):
        yield i


# arguments
parser = argparse.ArgumentParser(description="Solves the sudoku puzzle.")

# generic arguments
parser.add_argument('--method',
                    choices=searchtoy.blind_methods,
                    default='DepthFirst',
                    help='the search method to be used')

parser.add_argument('--solution-type', dest='solution_type',
                    choices=['first', 'all', 'optimal'],
                    default='first',
                    help='the type of solution required')

# problem-specific arguments
parser.add_argument('-f', '--filename', required=True,
                    help='the name of the file containing the puzzle')

parser.add_argument('--most-constrained', dest='most_constrained',
                    help='flag, use domains to make branching decisions',
                    action='store_true')

settings = parser.parse_args()

# state class
state_class = sudokuState

# generator
if settings.most_constrained:
    state_class.attach(MostConstrainedGenerator)
else:
    state_class.attach(SequentialGenerator)

# problem
problem = searchtoy.Problem(state_class.from_file(settings.filename),
                            state_class.is_complete)

# method
method = getattr(searchtoy, settings.method)()

# solve (a single solution is sufficient)
solution = problem.solve(method)
print(solution.state)
print("explored", method.nb_explored, "states")
