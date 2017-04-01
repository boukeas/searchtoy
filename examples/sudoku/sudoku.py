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
        
    __slots__ = ('board', 'nb_placed')
    
    def __init__(self, filename):
        self.board = board(9)
        self.nb_placed = 0
        for row in range(9):
            for col in range(9):
                self.board[row, col] = set(range(1, 10))
        if filename is not None:
            self.inputFromFile(filename)

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
        return "".join([str(self.board[row, col]) if type(self.board[row, col]) else "." for row in range(9) for col in range(9)]).__hash__()

    def copy(self):
        """ Returns a new state object that is a copy of self.
        """
        new_object = type(self).empty()
        new_object.nb_placed = self.nb_placed
        new_object.board = self.board.copy()
        return new_object

    def inputFromFile(self, filename):
        """
        """
        try:
            f = open(filename)
        except:
            print("error: unable to open file", filename)
            return None
            
        for row in range(9):
            line = f.readline()
            for col in range(9):
                if line[col] != ".":
                    number = int(line[col])
                    #print("error: invalid input at row:", row + 1, "col: ", col + 1)                    
                    self.place(row, col, number)

    def is_complete(self):
        """
        """
        return self.nb_placed == 81

    def affectedSquares(self, the_row, the_col):
        """
        """
        affected = set()
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
        self.board[the_row, the_col] = number
        self.nb_placed += 1
        for row, col in self.affectedSquares(the_row, the_col):
            domain = self.board[row, col]
            if type(domain) is set:
                domain.discard(number)

# generation of successor states

class SequentialGenerator(searchtoy.ConsistentGenerator):

    requires = sudokuState
    graph = False

    @staticmethod
    def selectSquare(state):
        for row in range(9):
            for col in range(9):
                if type(state.board[row, col]) is set:
                    return row, col

    @classmethod
    def operations(cls, state):
        row, col = cls.selectSquare(state)
        domain = state.board[row, col]
        for number in domain:
            yield state.operators.place(row, col, number)


class MostConstrainedGenerator(SequentialGenerator):

    requires = sudokuState
    graph = True

    @staticmethod
    def selectSquare(state):
        _, position = min((len(state.board[row, col]), (row, col))
                          for row in range(9)
                          for col in range(9)
                          if type(state.board[row, col]) is set)
        return position

# auxillary

class board:
    """ An n x n board.
    """

    __slots__ = ('size', 'container')

    def __init__(self, n, init = None):
        self.size = n
        self.container = {
            (row, col) : init
            for row in range(n)
            for col in range(n) 
        }

    def __getitem__(self, coords):
        """ Returns the value at coords (which is a row, col pair).
        """
        return self.container[coords]

    def __setitem__(self, coords, value):
        """ Sets the value at coords (which is a row, col pair).
        """
        self.container[coords] = value

    def copy(self):
        """
        """
        new_board = type(self).__new__(type(self))
        new_board.size = self.size
        new_board.container = {}
        for key, value in self.container.items():
            if type(value) is int:
                new_board.container[key] = value
            else:
                new_board.container[key] = value.copy()
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

# problem and method

if settings.most_constrained:
    state_class = sudokuState
    state_class.attach(MostConstrainedGenerator)
    problem = searchtoy.Problem(state_class(settings.filename), state_class.is_complete)
    method = getattr(searchtoy, settings.method)()
else:
    state_class = sudokuState
    state_class.attach(SequentialGenerator)
    problem = searchtoy.Problem(state_class(settings.filename), state_class.is_complete)
    method = getattr(searchtoy, settings.method)()

if settings.solution_type == 'all':

    for solution in problem.solutions(method):
        print(solution.state, end="\n\n")

    print("explored", method.nb_explored, "states")
    print("found", method.nb_solutions, "solutions")

else:

    solution = problem.solve(method)
    print(solution.state, end="\n\n")

    print("explored", method.nb_explored, "states")
