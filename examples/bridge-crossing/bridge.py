"""
BRIDGE CROSSING AT NIGHT
(description from Algorithmic Puzzles, by Anany and Maria Levitin)

Four people need to cross a rickety footbridge; they all begin on the same
side. It is dark, and they have one flashlight. A maximum of two people
can cross the bridge at one time. Any party that crosses, either one or two
people, must have the flashlight with them. The flashlight must be walked
back and forth; it cannot be thrown, for example. Person 1 takes 1 minute
to cross the bridge, person 2 takes 2 minutes, person 3 takes 5 minutes,
and person 4 takes 10 minutes. A pair must walk together at the rate of the
slower person’s pace. For example, if person 1 and person 4 walk together,
it will take them 10 minutes to get to the other side. If person 4 returns the
flashlight, a total of 20 minutes have passed. Can they cross the bridge in
17 minutes?


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
from itertools import combinations
from collections import OrderedDict

import searchtoy


# representation of problem-specific state

class crossState(searchtoy.State):
    """ Instances of the crossState class hold the current state of the
        bridge-crossing problem.

        The representation is not limited to four persons or specific
        crossing times.

        Attribute (in slots):

            positions: an ordered dict mapping the positions of the persons
                (or rather, their crossing times) and the flashlight to the
                values 'back' or 'across'.
    """

    __slots__ = ('positions')

    # class attribute to help with quickly reversing the positions of the actors
    reverse = {"back": "across", "across": "back"}

    def __init__(self, costs = (1, 2, 5, 10)):
        self.positions = OrderedDict((who,"back") for who in sorted(costs))
        self.positions["flashlight"] = "back"

    def __str__(self):
        """ Returns a "nicely printable" string representation of the state.
        """
        return "\n".join([side + ": " +
                          ", ".join(str(who)
                                        for who, where in self.positions.items()
                                        if where == side)
                          for side in ("back", "across")])

    def __hash__(self):
        """ Returns a unique integer computed from the current state.
        """
        return "".join("b" if position == "back" else "a"
                       for position in self.positions.values()).__hash__()

    def all_across(self):
        """ Returns True when all actors have crossed the bridge, or False
            otherwise.
        """
        # return all(self.positions[who] == "across" for who in self.positions)
        return "back" not in self.positions.values()

    # operators or operator-related methods

    @searchtoy.operator
    def cross(self, who):
        """ One of the persons crosses alone, carrying the flashlight.
        """
        self.positions[who] = self.positions["flashlight"] = self.reverse[self.positions["flashlight"]]

    @searchtoy.operator
    def escort(self, one, another):
        """ A pair crosses the bridge, carrying the flashlight.
        """
        self.positions[one] = self.positions[another] = self.positions["flashlight"] = self.reverse[self.positions["flashlight"]]

    # auxillary and generator-related methods

    @property
    def flashlight(self):
        """ Returns the side the flashlight is on.
        """
        return self.positions["flashlight"]

    def on_side(self, side):
        """ Yields the persons on a particular side.

            Note that, in the current implementation, persons are sorted during
            __init__ and that order is preserved by on_side(), since an
            OrderedDict is used to represent the state.
        """
        return (who for who in self.positions
                if self.positions[who] == side and who != "flashlight")


# generating successor states

class SoloFirstGenerator(searchtoy.ConsistentGenerator):
    """ Generates all possible operations applicable to a particular state.
    """

    graph = True
    requires = crossState

    @classmethod
    def operations(cls, state):
        """ Yields the operations that can be performed on a state.

            In this case, operations involve either one or two persons crossing
            the bridge with the flashlight. Note that solo crossings are yielded
            before paired ones and that affects the number of nodes generated.
        """
        for one in state.on_side(state.flashlight):
            yield state.operators.cross(one, cost=one)
        for one, another in combinations(state.on_side(state.flashlight), 2):
            yield state.operators.escort(one, another,
                                         cost=max(one, another))

class PairsFirstGenerator(searchtoy.ConsistentGenerator):
    """ Generates all possible operations applicable to a particular state.
    """

    graph = True
    requires = crossState

    @classmethod
    def operations(cls, state):
        """ Yields the operations that can be performed on a state.

            In this case, operations involve either one or two persons crossing
            the bridge with the flashlight. Note that pair crossings are yielded
            before solo ones and that affects the number of nodes generated.
        """
        for one, another in combinations(state.on_side(state.flashlight), 2):
            yield state.operators.escort(one, another,
                                         cost=max(one, another))
        for one in state.on_side(state.flashlight):
            yield state.operators.cross(one, cost=one)


class AdaptiveGenerator(searchtoy.ConsistentGenerator):
    """ Generates all possible operations applicable to a particular state.
    """

    graph = True
    requires = crossState

    @classmethod
    def operations(cls, state):
        """ Yields the operations that can be performed on a state.

            In this case, operations involve either one or two persons crossing
            the bridge with the flashlight. Note that pair crossings are
            yielded first when crossing the bridge, while solo crossings are
            yielded first when crossing back.
        """
        if state.flashlight == 'back':
            for one, another in combinations(state.on_side(state.flashlight), 2):
                yield state.operators.escort(one, another,
                                             cost=max(one, another))
            for one in state.on_side(state.flashlight):
                yield state.operators.cross(one, cost=one)
        else:
            for one in state.on_side(state.flashlight):
                yield state.operators.cross(one, cost=one)
            for one, another in combinations(state.on_side(state.flashlight), 2):
                yield state.operators.escort(one, another,
                                             cost=max(one, another))


# command-line arguments
parser = argparse.ArgumentParser(description="Solves the bridge crossing at night problem.")

# generic arguments
parser.add_argument('--method',
                    choices=searchtoy.blind_methods,
                    default='DepthFirst',
                    help='the search method to be used')

parser.add_argument('--solution-type', dest='solution_type',
                    choices=['first', 'all', 'optimal'],
                    default='first',
                    help='the type of solution required')

parser.add_argument('-u', '--upper-bound', dest='upper_bound',
                    type=int,
                    help="an upper bound on the solution's cost")

# problem-specific arguments

parser.add_argument('-g', '--generator',
                    choices=['solo', 'pairs', 'adaptive'],
                    default='solo',
                    help='the generator used for generating successor states')

settings = parser.parse_args()

# state class
state_class = crossState

# generator
if settings.generator == 'solo':
    state_class.attach(SoloFirstGenerator)
elif settings.generator == 'pairs':
    state_class.attach(PairsFirstGenerator)
else:
    state_class.attach(AdaptiveGenerator)

# problem
problem = searchtoy.Problem(state_class(), state_class.all_across)

# method
method = getattr(searchtoy, settings.method)()

# solve, according to solution type required
if settings.solution_type == 'all':

    for solution in problem.solutions(method, upper_bound=settings.upper_bound):
        for state, operation in solution.path:
            print(state, operation, end='\n\n')
        print(solution.state, " [", solution.cost, "]", sep="")

    print("explored", method.nb_explored, "states")
    print("found", method.nb_solutions, "solutions")

else:

    if settings.solution_type == 'optimal':
        solution = problem.optimize(method, upper_bound=settings.upper_bound)
    else:
        solution = problem.solve(method, upper_bound=settings.upper_bound)

    for state, operation in solution.path:
        print(state, operation, end='\n\n')
    print(solution.state, " [", solution.cost, "]", sep="")

    print("explored", method.nb_explored, "states")
