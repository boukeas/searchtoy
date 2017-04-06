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
    """ Instances of the tourState class hold the current state of the knight's
        tour problem.

        A ConsistentGenerator is used as a mixin class, adding the generator's
        method (i.e operations()) to tourState's interface. Therefore, tourState
        can produce its own successors without the need to construct an explicit
        generator and attach it.

        Attributes (in slots):

            nb_hops: the number of hops the knight has performed
            current: a pair of integers, indicating the knight's position
            positions: a dict holding pairs of positions and hop numbers, e.g.
                (3,6):15 if the 15th hop was in position (3,6).
    """
    __slots__ = ('nb_hops', 'current', 'positions')

    # class attribute with 8 pairs of horizontal and vertical offsets,
    # corresponding to the 8 moves available to a knight on the board
    hops = ((2, 1), (2, -1), (1, -2), (-1, -2),
            (-2, -1), (-2, 1), (-1, 2), (1, 2))

    def __init__(self, start_row, start_col):
        self.nb_hops = 0
        self.current = (start_row, start_col)
        self.positions = {self.current: 0}

    def __str__(self):
        """ Returns a "nicely printable" string representation of the state.
        """
        return "\n".join(" ".join("%2s" % self.positions.get((row, col), "..")
                         for col in range(8)) for row in range(8))

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

    # operators and operator-related methods

    def is_complete(self):
        """ Returns True if the current state corresponds to a complete knight's
            tour and False otherwise.
        """
        return self.nb_hops == 63

    def is_available(self, row, col):
        """ Returns True if position (row, col) is available and False otherwise.
        """
        return (row, col) not in self.positions

    def accessible(self, the_row, the_col):
        """ Yields a list of positions, i.e. (row, col) pairs that are available
            for a knight's hop, starting from the_row, the_col.
        """
        for row_offset, col_offset in tourState.hops:
            row, col = the_row + row_offset, the_col + col_offset
            if (0 <= row < 8 and 0 <= col < 8 and self.is_available(row, col)):
                yield row, col

    @searchtoy.operator
    def hop(self, the_row, the_col):
        """ The knight hops to the_row, the_col from its current position.
        """
        self.nb_hops += 1
        self.current = (the_row, the_col)
        self.positions[self.current] = self.nb_hops

    # generator-related methods

    def operations(self):
        """ Yields the operations that can be performed on a state.

            In this case, operations involve the knight hoping to any of the
            squares that are accessible from its current position.
        """
        for row, col in self.accessible(*self.current):
            yield self.operators.hop(row, col)


# extended representation of problem-specific state

class WarnsdorfState(tourState):
    """ An extended representation of the knight's tour board that maintains,
        for each square of the board, an accessibility count, i.e. the number
        of squares from which the current square can be accessed. The idea
        comes from Deitel's "How to program C++" and essentially describes the
        Warnsdorf heuristic: https://en.wikipedia.org/wiki/Knight%27s_tour

        The accessibility count in this extended representation can be directly
        used as an evaluation function for heuristically guiding the search.
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
        """ The knight hops to the_row, the_col and all the squares accessible
            from this new position have their accessibility count reduced by 1,
            because when the knight leaves this position, there will be one less
            way for them to be reached.
        """
        super().hop(the_row, the_col)
        self.accessibility[self.current] = 0
        for row, col in self.accessible(the_row, the_col):
            self.accessibility[(row, col)] -= 1


@searchtoy.evaluator(requires=WarnsdorfState)
def Warnsdorf(node):
    """ An evaluation function utilizing the accessibility table in the
        WarnsdorfState class. It returns the accessibility count of
        the current position in *the parent* of the evaluated node. Think about
        this for a minute: from a given position, this will select the
        successor node with the lowest accessibility.
    """
    return node.parent.state.accessibility[node.state.current]


# arguments
parser = argparse.ArgumentParser(description="Finds the knight's tour on an 8x8 board.")

# generic arguments

parser.add_argument('--method',
                    choices=searchtoy.methods,
                    default='DepthFirst',
                    help='the search method to be used')

# problem-specific arguments

parser.add_argument('-i', '--initial',
                    required=True, nargs=2, type=int, metavar=('row','col'),
                    help='row and col where the knight is initially placed')

settings = parser.parse_args()

# state class, problem and method
row, col = settings.initial
if settings.method in searchtoy.blind_methods:
    state_class = tourState
    problem = searchtoy.Problem(state_class(row, col), state_class.is_complete)
    method = getattr(searchtoy, settings.method)()
else:
    state_class = WarnsdorfState
    problem = searchtoy.Problem(state_class(row, col), state_class.is_complete)
    method = getattr(searchtoy, settings.method)(evaluator=Warnsdorf)
    
# solve (a single solution is sufficient)
solution = problem.solve(method)
print(solution.state, end="\n\n")
print("explored", method.nb_explored, "states")
