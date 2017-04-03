"""
THE SWAP PUZZLE

(The description is adapted from the excellent unplugged activity at:
https://teachinglondoncomputing.org/resources/inspiring-unplugged-classroom-activities/the-swap-puzzle-activity/,
although many online versions of the puzzle are also available.)

The puzzle board is a linear array of 2*N + 1 squares. Start the game with N red
pieces at one end of the board and N blue pieces at the other, with each square
occupied by a single piece. The square in the middle should be the only square
left empty at the start.

Here's an example of the initial configuration, on a board with 7 squares,
with 3 red pieces (denoted 'x') and 3 blue pieces (denoted 'o'):

    [ x | x | x |   | o | o | o ]

The aim of the game is to swap the position of the blue pieces with those of the
red pieces. You must do it in as few moves as possible.

There are two kinds of move:
1. Move a piece to an adjacent empty square (forwards or backwards).
2. Jump a single adjacent piece of any colour into an empty space (forwards or
backwards).

Here's an example of the final configuration, on a board with 7 squares:

    [ o | o | o |   | x | x | x ]


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
from collections import defaultdict

import searchtoy


# representation of problem-specific state

class swapState(searchtoy.State):
    """ Instances of the swapState class hold the current state of the
        swap puzzle.

        Attributes (in slots):
            puzzle: a list, with each element corresponding to a board square
            gap: the index of the empty square

        Class Attributes:
            size: the length of the board
            target: the goal state
    """
    __slots__ = ('puzzle', 'gap')

    size = None
    target = None

    def __init__(self, size, symbol_left = "x", symbol_right = "o"):
        self.puzzle = size * [symbol_left] + [" "] + size * [symbol_right]
        self.gap = size
        # set class attributes
        cls = type(self)
        cls.size = len(self.puzzle)
        cls.target = self.puzzle[::-1]

    def __str__(self):
        """ Returns a "nicely printable" string representation of the state.
        """
        return "[ {puzzle} ]".format(puzzle=" | ".join(self.puzzle))

    def __hash__(self):
        """ Returns a unique integer computed from the current state.
        """
        return "".join(self.puzzle).__hash__()

    def copy(self):
        """ Returns a new state object that is a copy of self.
        """
        new_object = type(self).empty()
        new_object.puzzle = self.puzzle.copy()
        new_object.gap = self.gap
        return new_object

    # operators and operator-related methods

    def is_target(self):
        """ Returns true if the current state of the puzzle is the goal state,
            and False otherwise.
        """
        return self.puzzle == self.target

    def move(self, which):
        """ Swaps the gap with the contents of the square at the specified index.
        """
        swap(self.puzzle, self.gap, which)
        self.gap = which

    @searchtoy.action
    def slide_right(self):
        self.move(self.gap - 1)

    @searchtoy.action
    def slide_left(self):
        self.move(self.gap + 1)

    @searchtoy.action
    def jump_right(self):
        self.move(self.gap - 2)

    @searchtoy.action
    def jump_left(self):
        self.move(self.gap + 2)


# generation of successor states

class obviousGenerator(searchtoy.ConsistentGenerator):
    """ Generates all possible operations applicable to a particular state.
    """
    requires = swapState
    graph = True

    @classmethod
    def operations(cls, state):
        """ Yields the operations that can be performed on a state.

            In this case, operations involve sliding any of the two pieces that
            lie next to the empty square, or jumping above any of those two
            pieces. Note that when two consecutive squares next to the empty
            square are occupied by pieces of the same color, it makes no sense
            to differentiate between sliding and jumping.

            The method first yields operations that make left-to-right moves
            and then right-to-left moves.
        """
        gap = state.gap
        # moves (slides and jumps) left to right
        if gap > 1:
            yield state.operators.slide_right()
            if state.puzzle[gap - 1] != state.puzzle[gap - 2]:
                yield state.operators.jump_right()
        elif state.gap == 1:
            yield state.operators.slide_right()
        # moves (slides and jumps) right to left
        if gap < state.size - 2:
            yield state.operators.slide_left()
            if state.puzzle[gap + 1] != state.puzzle[gap + 2]:
                yield state.operators.jump_left()
        elif state.gap == state.size - 2:
            yield state.operators.slide_left()

class jumpyGenerator(searchtoy.ConsistentGenerator):
    """ Generates all possible operations applicable to a particular state.
    """
    requires = swapState
    graph = True

    @classmethod
    def operations(cls, state):
        """ Yields the operations that can be performed on a state.

            In this case, operations involve sliding any of the two pieces that
            lie next to the empty square, or jumping above any of those two
            pieces. Note that when two consecutive squares next to the empty
            square are occupied by pieces of the same color, it makes no sense
            to differentiate between sliding and jumping.

            The method first yields moves than involve jumps and then slides.
        """
        gap = state.gap
        # jump left to right
        if gap > 1:
            if state.puzzle[gap - 1] != state.puzzle[gap - 2]:
                yield state.jump_right()
        # jump right to left
        if gap < state.size - 2:
            if state.puzzle[gap + 1] != state.puzzle[gap + 2]:
                yield state.jump_left()
        # slide left to right
        if gap > 0:
            yield state.slide_right()
        # slide right to left
        if gap < state.size - 1:
            yield state.slide_left()


# state evaluation

@searchtoy.evaluator(requires=swapState)
def distance(node):
    """ Returns the distance between the node and the target state. The distance
        is the sum of offsets of every single piece from its target position.
    """
    # make occurrences_target a class attribute, shouldn't recompute every time
    # compute the squares where each symbol occurs in node
    occurences = defaultdict(list)
    for i, symbol in enumerate(node.state.puzzle):
        occurences[symbol].append(i)
    # compute the squares where each symbol occurs in the target
    occurences_target = defaultdict(list)
    for i, symbol in enumerate(node.state.target):
        occurences_target[symbol].append(i)
    # compute the sum of distances
    d = 0
    for symbol, positions in occurences.items():
        positions_target = occurences_target[symbol]
        for index1, index2 in zip(positions, positions_target):
            d += abs(index1 - index2 + 1)
    return d


# auxillary

def swap(l, a, b):
    l[a], l[b] = l[b], l[a]


# arguments
parser = argparse.ArgumentParser(description="Solves the swap puzzle of size n")

# generic arguments

parser.add_argument('--method',
                    choices=searchtoy.methods,
                    default='DepthFirst',
                    help='the search method to be used')

parser.add_argument('--solution-type', dest='solution_type',
                    choices=['first', 'all', 'optimal'],
                    default='first',
                    help='the type of solution required')

# problem-specific arguments

parser.add_argument('-n', '--size', type=int,
                    required=True,
                    help='the size n of the swap puzzle (the number of tiles)')

parser.add_argument('--jumpy',
                    help='flag, try jumps before sliding',
                    action='store_true')

settings = parser.parse_args()

# state class
state_class = swapState

# generator
if settings.jumpy:
    state_class.attach(jumpyGenerator)
else:
    state_class.attach(obviousGenerator)

# problem
problem = searchtoy.Problem(state_class(settings.size), state_class.is_target)

# method
if settings.method in searchtoy.blind_methods:
    method = getattr(searchtoy, settings.method)()
else:
    method = getattr(searchtoy, settings.method)(evaluator=distance)

# solve, according to solution type required
if settings.solution_type == 'all':

    for solution in problem.solutions(method):
        for state, operation in solution.path:
            print(state, operation)
        print(solution.state, solution.cost, end="\n\n")

    print("explored", method.nb_explored, "states")
    print("found", method.nb_solutions, "solutions")

else:

    if settings.solution_type == 'optimal':
        solution = problem.optimize(method)
    else:
        solution = problem.solve(method)

    for state, operation in solution.path:
        print(state, operation)
    print(solution.state, solution.cost, end="\n\n")

    print("explored", method.nb_explored, "states")
