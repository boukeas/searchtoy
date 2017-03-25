"""
THE N-QUEENS PROBLEM

The n-Queens Problem Place n queens on an n × n chessboard so that no two queens
attack each other by being in the same column, row, or diagonal.

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

class QueensState(searchtoy.State, searchtoy.ConsistentGenerator, graph=False):
    """ Representation of an arbitrary-sized board for the N-queens problem.

        Class attribute:
            size: the number of queens

        Attribute (in slots):
            rows: a list, with an element for every row, and its value
                corresponding to the column in which a queen is placed
                (or None, if the row is not occupied by a queen).
    """
    __slots__ = ('rows')

    # the size of the board (class attribute)
    size = None

    def __init__(self, size):
        type(self).size = size
        self.rows = [None] * size

    def __str__(self):
        """ Returns a "nicely printable" string representation of the state.
        """
        return "\n".join(row * '. ' + 'Q' + (self.size - row - 1) * ' .'
                         if row is not None else self.size * '. '
                         for row in self.rows)

    def __hash__(self):
        """ Returns a unique integer computed from the current state.
        """
        return "".join(str(row)
                       if row is not None else "."
                       for row in self.rows).__hash__()

    def is_complete(self):
        """ Checks whether there is a queen in every row.
        """
        return not any(row is None for row in self.rows)

    def copy(self):
        """ Returns a new state object that is a copy of self.
        """
        new_object = type(self).empty()
        new_object.rows = self.rows.copy()
        return new_object

    # operator-related methods

    @searchtoy.operator
    def place(self, the_row, the_col):
        """ Places a queen at the_row, the_col.
        """
        self.rows[the_row] = the_col

    # generator-related methods

    @staticmethod
    def affected(the_row, the_col, *, size):
        """ Yields row, col pairs of the chessboard squares **above** the_row
            that are affected (threatened) by a queen in the_row, the_col.
        """

        # vertical check, for rows above the_row
        for row in range(the_row):
            yield row, the_col

        # primary diagonal check, for rows above the_row
        d = the_row - the_col
        if d >= 0:
            for row in range(d, the_row):
                yield row, row - d
        else:
            for col in range(-d, the_col):
                yield col + d, col

        # secondary diagonal check, for rows above the_row
        d = size - 1 - (the_row + the_col)
        if d >= 0:
            for row in range(the_row):
                yield row, size - d - 1 - row
        else:
            for row in range(-d, the_row):
                yield row, size - d - 1 - row
 
    def operations(self):
        """ Yields the operations that can be performed on a state.

            In this case, the operations are all legal queen placements on the
            first available row.
        """
        the_row = self.rows.index(None)
        for the_col in range(self.size):
            for row, col in self.affected(the_row, the_col, size=self.size):
                if self.rows[row] == col:
                    break
            else:
                yield self.operators.place(the_row, the_col)


# extended representation of problem-specific state

class QueensDomainsState(QueensState, graph=True):
    """ Extended representation of the N-Queens problem board.

        This representations includes the "domains" for every row, i.e. the
        sets of columns where a queen can be legally placed. The domains are
        updated each time a new queen is placed. This additional information
        can be used by generators in order to first select rows that are
        most constrained, i.e. have the fewest possible choices.

        Attribute (in slots):
            domains: a tuple, with a set for every row, containing the columns
                than can be legally occupied by a queen.
    """

    __slots__ = ('domains')

    def __init__(self, size):
        super().__init__(size)
        self.domains = tuple(set(range(self.size)) for domain in range(self.size))

    def __str__(self):
        """ Returns a "nicely printable" string representation of the state.
        """
        return "\n".join(row * 'x ' + 'Q' + (self.size - row - 1) * ' x'
                         if row is not None else
                         " ".join("." if col in domain else "x"
                                  for col in range(self.size))
                         for row, domain in zip(self.rows, self.domains))

    def copy(self):
        """ Returns a new state object that is a copy of self.
        """
        new_object = super().copy()
        new_object.domains = tuple(domain.copy() for domain in self.domains)
        return new_object

    # operator-related methods

    @searchtoy.operator
    def place(self, the_row, the_col):
        """ Places a queen at the_row, the_col.
        """
        super().place(the_row, the_col)

        # discard all other columns from the_row's domain
        for col in skiprange(0, self.size, skip=the_col):
            self.domains[the_row].discard(col)

        # propagate the effect to the domains of other rows
        for row, col in self.affected(the_row, the_col, size=self.size):
            self.domains[row].discard(col)

    # generator-related methods

    @staticmethod
    def affected(the_row, the_col, *, size):
        """ Yields row, col pairs of the chessboard squares that are affected
            (threatened) by a queen in the_row, the_col.
        """
        # vertical check, for all rows except the_row
        for row in skiprange(0, size, skip=the_row):
            yield row, the_col

        # primary diagonal check
        d = the_row - the_col
        if d >= 0:
            for row in skiprange(d, size, skip=the_row):
                yield row, row - d
        else:
            for col in skiprange(-d, size, skip=the_col):
                yield col + d, col

        # secondary diagonal check
        d = size - 1 - (the_row + the_col)
        if d >= 0:
            for row in skiprange(0, size - d, skip=the_row):
                yield row, size - d - 1 - row
        else:
            for row in skiprange(-d, size, skip=the_row):
                yield row, size - d - 1 - row

    def operations(self):
        """ Yields the operations that can be performed on a state.

            In this case, the operations are all legal queen placements on the
            first available row with the smallest domain.
        """
        # find the row with the smallest domain
        _, the_row = min((len(domain), row)
                         for row, (col, domain) in enumerate(zip(self.rows, self.domains))
                         if col is None)

        # successors generated by placing a queen in every column in the domain
        for the_col in self.domains[the_row]:
            yield self.operators.place(the_row, the_col)


# auxillary

def skiprange(start, end, *, skip):
    """ Yields the integers in the ranges [start, skip) and (skip, end).
    """
    for i in range(start, skip):
        yield i
    for i in range(skip + 1, end):
        yield i



# arguments
parser = argparse.ArgumentParser(description="Solves the N-Queens problem.")

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

parser.add_argument('--size', type=int,
                    default=8,
                    help='the size n of the n x n board')

parser.add_argument('--domains',
                    help='flag, use column domains to make branching decisions',
                    action='store_true')

settings = parser.parse_args()

# problem and method

if settings.domains: 
    state_class = QueensDomainsState
else:
    state_class = QueensState

problem = searchtoy.Problem(state_class(settings.size), state_class.is_complete)
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

