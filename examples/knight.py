"""
THE KNIGHT'S TOUR

Starting from any initial position, use a knight to visit all the squares of a
chessboard exactly once.


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

import random
import argparse

import searchtoy


# representation of problem-specific state

class tourState(searchtoy.State, searchtoy.ConsistentGenerator, graph=True):
    """
    """

    __slots__ = ('nb_hops', 'current', 'positions')

    hops = ((2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1), (-2, 1), (-1, 2), (1, 2))

    def __init__(self, start_row, start_col):
        self.nb_hops = 0
        self.current = (start_row, start_col)
        self.positions = {self.current: 0}

    def __str__(self):
        """ Returns a "nicely printable" string representation of the state.
        """
        return "\n".join(" ".join("%2s" % self.positions.get((row, col), "..") for col in range(8)) for row in range(8))

    def __hash__(self):
        """ Returns a unique integer computed from the current state.
        """
        return self.__str__().__hash__()        

    def copy(self):
        """ Returns a new state object that is a copy of self.
        """
        new_object = type(self).empty()
        new_object.nb_hops = self.nb_hops
        new_object.current = self.current
        new_object.positions = self.positions.copy()
        return new_object

    #

    def is_complete(self):
        """
        """
        return self.nb_hops == 63

    def is_available(self, row, col):
        return (row, col) not in self.positions

    def accessible(self, the_row, the_col):
        for row_offset, col_offset in tourState.hops:
            row, col = the_row + row_offset, the_col + col_offset
            if (0 <= row < 8 and 0 <= col < 8 and self.is_available(row, col)):
                yield row, col

    # operator-related methods

    @searchtoy.operator
    def hop(self, the_row, the_col):
        """
        """
        self.nb_hops += 1
        self.current = (the_row, the_col)
        self.positions[self.current] = self.nb_hops

    # generator-related methods

    def operations(self):
        """
        """
        for row, col in self.accessible(*self.current):
            yield self.operators.hop(row, col)


# extended representation of problem-specific state

class WarnsdorfState(tourState):
    """
    """

    __slots__ = ('accessibility')

    def __init__(self, start_row, start_col):
        super().__init__(start_row, start_col)
        self.accessibility = {(row, col): len(list(self.accessible(row, col)))
                              for row in range(8) for col in range(8)}
        self.accessibility[self.current] = 0

    def copy(self):
        """ Returns a new state object that is a copy of self.
        """
        new_object = super().copy()
        new_object.accessibility = self.accessibility.copy()
        return new_object

    @searchtoy.operator
    def hop(self, the_row, the_col):
        """
        """
        super().hop(the_row, the_col)
        self.accessibility[self.current] = 0
        for row, col in self.accessible(the_row, the_col):
            self.accessibility[(row, col)] -= 1


'''
# state evaluation
class accessibilityEvaluator(search.Evaluator):

    # https://en.wikipedia.org/wiki/Knight%27s_tour

    def evaluate(self, node):
        row, col = node.state.current
        value = node.parent.state.accessibility[(row, col)]
        return value
'''

@searchtoy.evaluator
def Warnsdorf(node):
    return node.parent.state.accessibility[node.state.current]


# arguments
parser = argparse.ArgumentParser(description="Solves the knight's tour problem on an 8x8 chessboard.")

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

parser.add_argument('--accessibility',
                    help='flag, use the Warnsdorf heuristic',
                    action='store_true')


settings = parser.parse_args()

# problem and method

if settings.accessibility:
    state_class = WarnsdorfState
    problem = searchtoy.Problem(state_class(3,5), state_class.is_complete)
    method = getattr(searchtoy, settings.method)(evaluator=Warnsdorf)
else:
    state_class = tourState
    problem = searchtoy.Problem(state_class(3,5), state_class.is_complete)
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
