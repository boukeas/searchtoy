"""
THE SWAP PUZZLE


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
    """
    """

    __slots__ = ('puzzle', 'gap')

    size = None
    target = None

    def __init__(self, size, symbol_left = "x", symbol_right = "o"):
        self.puzzle = size * [symbol_left] + [" "] + size * [symbol_right]
        self.gap = size
        #
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

    # operator-related methods

    def is_target(self):
        return self.puzzle == self.target

    def min_index(self):
        return max(0, self.gap - 2)

    def max_index(self):
        return min(len(self.puzzle), self.gap + 3)

    def move(self, which):
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
    """
    """

    requires = swapState
    graph = True

    @classmethod
    def operations(cls, state):
        """ Yields the operations that can be performed on a state.

            In this case...
        """
        gap = state.gap
        # moves left to right
        if gap > 1:
            yield state.operators.slide_right()
            if state.puzzle[gap - 1] != state.puzzle[gap - 2]:
                yield state.operators.jump_right()
        elif state.gap == 1:
            yield state.operators.slide_right()
        # moves right to left
        if gap < state.size - 2:
            yield state.operators.slide_left()
            if state.puzzle[gap + 1] != state.puzzle[gap + 2]:
                yield state.operators.jump_left()
        elif state.gap == state.size - 2:
            yield state.operators.slide_left()

class jumpyGenerator(searchtoy.ConsistentGenerator):
    """
    """

    requires = swapState
    graph = True

    def operations(self, state):
        """ Yields the operations that can be performed on a state.

            In this case...
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

# make occurrences_target a class attribute, you don't have to recompute every time
@searchtoy.evaluator(requires=swapState)
def distance(node):
    """
    """
    occurences = defaultdict(list)
    for i, symbol in enumerate(node.state.puzzle):
        occurences[symbol].append(i)
    occurences_target = defaultdict(list)
    for i, symbol in enumerate(node.state.target):
        occurences_target[symbol].append(i)

    distance = 0
    for symbol, positions in occurences.items():
        positionsTarget = occurences_target[symbol]
        for i in range(len(positions)):
            distance += abs(positions[i] - positionsTarget[i])
    
    return distance


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

parser.add_argument('--distance',
                    help='flag, use distance from target heuristic for guiding search',
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
if settings.distance:
    method = getattr(searchtoy, settings.method)(evaluator=distance)
else:
    method = getattr(searchtoy, settings.method)()

# solve
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
