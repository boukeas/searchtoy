"""
THE SLIDING TILES PUZZLE (a.k.a. 8-puzzle, 15-puzzle, etc)
(adapted from Algorithmic Puzzles, by Anany and Maria Levitin)

This famous puzzle consists of n×n square tiles numbered from 1 to (n×n)-1
which are placed in a n×n box, leaving one square empty. The goal is to
reposition the tiles from a given starting arrangement by sliding them one at
a time into the configuration in which the tiles are ordered sequentially.


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
import random
from collections import defaultdict

import searchtoy


# representation of problem-specific state

class tilesState(searchtoy.State, searchtoy.ConsistentGenerator):
    """ Instances of the tilesState class hold the current state of the
        sliding tiles puzzle.

        Class attributes:

            size: the length of the side of the puzzle
            target: the target state for the puzzle
            blank_element: the symbol for the blank tile

        Attribute (in slots):

            tiles: a list of size**2 elements, holding the puzzle's contents
            blank: the index of the 'hole', the missing tile
    """

    __slots__ = ('tiles', 'blank')

    size = None
    target = None
    blank_element = None

    def __init__(self, size, init, blank_element = 0):
        cls = type(self)
        cls.size = size
        cls.blank_element = blank_element
        nb_tiles = self.size ** 2
        self.tiles = list(init)[:nb_tiles]
        self.blank = self.tiles.index(self.blank_element)
        # the target is **always** the sorted list of tiles,
        # with the blank tile last, i.e. on the lower left corner
        cls.target = sorted(self.tiles[:self.blank] +
                            self.tiles[self.blank+1:]) + [self.blank_element]

    @staticmethod
    def fromFile(filename):
        """ Alternate constructor, returns a new tileState object from a file.

            Arguments:
                filename: name of the file containing the puzzle representation
        """
        ### warning: quick and dirty, absolutely no error checking here...
        ### doesn't even use is_solvable() to return an appropriate exception
        from math import sqrt

        with open(filename, 'rt') as f:
            data = f.read().strip().split()

        blank_element, puzzle = data[0], data[1:]
        size = int(sqrt(len(puzzle)))
        return tilesState(size, puzzle, blank_element)

    def __str__(self):
        """ Returns a "nicely printable" string representation of the state.
        """
        return "\n".join(" ".join("%2s" % str(tile)
                         if tile != self.blank_element else " ."
                         for tile in self.tiles[row*self.size:(row+1)*self.size])
                         for row in range(self.size))

    def __hash__(self):
        """ Returns a unique integer computed from the current state.
        """
        return "".join(str(tile) for tile in self.tiles).__hash__()

    def copy(self):
        """ Returns a new state object that is a copy of itself.
        """
        new_object = type(self).empty()
        new_object.tiles = self.tiles.copy()
        new_object.blank = self.blank
        return new_object

    def is_target(self):
        """ Returns True when the puzzle has reached the target state, or
            False otherwise.
        """
        return self.tiles == type(self).target

    def is_solvable(self):
        """ Returns True when the puzzle is solvable, or False otherwise.

            For details regarding when a sliding tile puzzle is solvable, see:
            www.cs.bham.ac.uk/~mdr/teaching/modules04/java2/TilesSolvability.html
        """
        inversions = defaultdict(int)
        for index, tile in enumerate(self.tiles[:-1]):
            for t_tile in self.tiles[index+1:]:
                if t_tile and t_tile < tile:
                    inversions[tile] += 1
        inversions = sum(inversions.values())
        from_last = self.size - self.blank_element // self.size
        return (self.size % 2 == 1 and inversions % 2 == 0 or
                self.size % 2 == 0 and inversions % 2 == 1 - from_last % 2)

    # action or action-related methods

    def move(self, which):
        # assumes the swap move is legal
        swap(self.tiles, self.blank, which)
        self.blank = which

    def left_possible(self):
        return self.blank % self.size != 0

    def right_possible(self):
        return self.blank % self.size != self.size - 1

    def up_possible(self):
        return self.blank // self.size != 0

    def down_possible(self):
        return self.blank // self.size != self.size - 1

    @searchtoy.action
    def left(self):
        self.move(self.blank - 1)

    @searchtoy.action
    def right(self):
        self.move(self.blank + 1)

    @searchtoy.action
    def up(self):
        self.move(self.blank - self.size)

    @searchtoy.action
    def down(self):
        self.move(self.blank + self.size)

    def operations(self):
        """ Yields the operations that can be performed on a state.

            In this case, operations involve sliding *the blank tile*
            left, right, up or down.
        """
        if self.left_possible():
            yield self.operators.left()
        if self.right_possible():
            yield self.operators.right()
        if self.up_possible():
            yield self.operators.up()
        if self.down_possible():
            yield self.operators.down()


# heuristic state evaluation

class manhattanEvaluator(searchtoy.Evaluator):
    """ Evaluates a sliding tile puzzle state using the manhattan distance.

        The manhattan distance of a single tile is the sum of its horizontal
        and vertical offset from its target position. The value of a sliding
        tile puzzle state is the sum of the manhattan distances of its tiles.
    """
    requires = tilesState

    @staticmethod
    def distance(i, j, size):
        return abs(i // size - j // size) + abs(i % size - j % size)

    @staticmethod
    def evaluate(node):
        return sum(manhattanEvaluator.distance(index,
                                               tilesState.target.index(tile),
                                               node.state.size)
                   for index, tile in enumerate(node.state.tiles))

# auxillary

def swap(c, a, b):
    """ Swaps two elements in an "indexable?" container.

        Arguments:
        - c: the container
        - a, b: the indices of the elements to be swapped
    """
    c[a], c[b] = c[b], c[a]


# command-line arguments
parser = argparse.ArgumentParser(description="Solves the sliding tile puzzle.")

# generic
parser.add_argument('--method',
                    choices=searchtoy.methods,
                    default='DepthFirst',
                    help='the search method to be used')

parser.add_argument('--solution-type', dest='solution_type',
                    choices=['first', 'all', 'optimal'],
                    default='first',
                    help='the type of solution required')

# problem-specific

parser.add_argument('-f', '--filename',
                    required=True,
                    help='the text file containing the initial puzzle')

settings = parser.parse_args()

# state class
state_class = tilesState

# problem
problem = searchtoy.Problem(tilesState.fromFile(settings.filename),
                            state_class.is_target)

# method
if settings.method in searchtoy.blind_methods:
    method = getattr(searchtoy, settings.method)()
else:
    method = getattr(searchtoy, settings.method)(evaluator=manhattanEvaluator)

# solve, according to solution type required
if settings.solution_type == 'all':

    for solution in problem.solutions(method):
        for state, operation in solution.path:
            print(state, operation, end='\n\n')
        print(solution.state, " [", solution.cost, "]", sep="")

    print("explored", method.nb_explored, "states")
    print("found", method.nb_solutions, "solutions")

else:

    if settings.solution_type == 'optimal':
        solution = problem.optimize(method)
    else:
        solution = problem.solve(method)

    for state, operation in solution.path:
        print(state, operation, end='\n\n')
    print(solution.state, " [", solution.cost, "]", sep="")

    print("explored", method.nb_explored, "states")
