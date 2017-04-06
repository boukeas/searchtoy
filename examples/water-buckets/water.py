"""
THE WATER BUCKETS PROBLEM

(Description is from http://www.openbookproject.net/py4fun/buckets/buckets.html
but see also https://en.wikipedia.org/wiki/Liquid_water_pouring_puzzles, as many
variations can be found.)

You go to the well with a 7 liter bucket and an 11 liter bucket. You wish to
fill one of them with exactly X liters of water. How can you do this in the
fewest number of operations, where each operation either fills or empties one
of the two buckets.


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

from itertools import permutations
import argparse

import searchtoy


# representation of problem-specific state

class bucketState(searchtoy.State, searchtoy.ConsistentGenerator):
    """ Instances of the bucketState class hold the current state of the
        water buckets problem.

        Attribute (in slots):

            positions: a dict holding the contents of each bucket. For
                convenience, the keys to the items of the dict are the bucket
                capacities.
    """
    __slots__ = ('buckets')

    def __init__(self, sizes):
        self.buckets = {size: 0 for size in sizes}

    def __str__(self):
        """ Returns a "nicely printable" string representation of the state.
        """
        return " | ".join(str(self.buckets[size]) + "/" + str(size) + " lt"
                         for size in sorted(self.buckets.keys()))

    def __hash__(self):
        """ Returns a unique integer computed from the current state.
        """
        return "".join(str(self.buckets[size])
                       for size in sorted(self.buckets.keys())).__hash__()

    def copy(self):
        """ Returns a new state object that is a copy of self.
        """
        new_object = type(self).empty()
        new_object.buckets = self.buckets.copy()
        return new_object

    # operators or operator-related methods

    def capacity(self, which):
        """ Returns the amount of water that remains empty in the bucket with
            the specified capacity.
        """
        return which - self.buckets[which]

    @searchtoy.operator
    def fill(self, which):
        """ Completely fills a bucket with the specified capacity.
        """
        self.buckets[which] = which

    @searchtoy.operator
    def drain(self, which):
        """ Completely empties a bucket with the specified capacity.
        """
        self.buckets[which] = 0

    @searchtoy.operator
    def pour(self, source, destination):
        """ Pours an amount of water from the source bucket to the destination
            bucket, until the former is empty, or the latter filled.
        """
        # this is the amount of water to be transfered
        transfer = min(self.capacity(destination), self.buckets[source])
        self.buckets[source] -= transfer
        self.buckets[destination] += transfer

    # generator-related methods

    def operations(self):
        """ Yields the operations that can be performed on a state.

            In this case, operations involve filling non-full buckets,
            emptying buckets with contents, or transfering water between
            buckets, where possible.
        """
        # for each bucket, fill it, if possible
        for bucket in self.buckets:
            if self.capacity(bucket) > 0:
                yield self.operators.fill(bucket)
        # for each bucket, empty it, if possible
        for bucket in self.buckets:
            if self.buckets[bucket] > 0:
                yield self.operators.drain(bucket)
        # for each pair of buckets, make a transfer, if possible
        for source, destination in permutations(self.buckets.keys(), 2):
            if self.buckets[source] > 0 and self.capacity(destination) > 0:
                yield self.operators.pour(source, destination)


# arguments
parser = argparse.ArgumentParser(description="Solves the 7-11 water buckets problem")

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

parser.add_argument('--buckets', type=int,
                    required=True,
                    nargs='*', metavar='CAPACITY',
                    help='the capacities of the buckets')

parser.add_argument('--target', type=int,
                    required=True,
                    help='the target amount of water in any bucket')

settings = parser.parse_args()

# state class
state_class = bucketState

# problem
problem = searchtoy.Problem(state_class(settings.buckets),
                            lambda state:settings.target in state.buckets.values())

# method
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
