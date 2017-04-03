"""
A WOLF, A GOAT AND A CABBAGE
(description from Algorithmic Puzzles, by Anany and Maria Levitin)

A man finds himself on a riverbank with a wolf, a goat, and a head of
cabbage. He needs to transport all three to the other side of the river in
his boat. However, the boat has room for only the man himself and one
other item (either the wolf, the goat, or the cabbage). In his absence, the
wolf would eat the goat, and the goat would eat the cabbage. Show how
the man can get all these "passengers" to the other side.


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
from collections import OrderedDict

import searchtoy


# representation of problem-specific state

class crossState(searchtoy.State, searchtoy.InconsistentGenerator):
    """ Instances of the crossState class hold the current state of the
        river-crossing problem.

        An InconsistentGenerator is used as a mixin class, adding the
        generator's methods (i.e operations() and is_valid()) to crossState's
        interface. Therefore, crossState can produce its own successors
        without the need to construct an explicit generator and attach it.

        Attribute (in slots):

            positions: an ordered dict mapping the positions of the 'farmer',
                the 'wolf', the 'cabbage' and the 'sheep' to the values 'left'
                or 'right'.
    """

    __slots__ = ('positions')

    # class attribute to help with quickly reversing the positions of the actors
    reverse = {"left": "right", "right": "left"}

    def __init__(self, farmer = "left", wolf = "left", cabbage = "left", sheep = "left"):
        self.positions = OrderedDict([("farmer", farmer), ("wolf", wolf),
                                      ("cabbage", cabbage), ("sheep", sheep)])

    def __str__(self):
        """ Returns a "nicely printable" string representation of the state.
        """
        return "\n".join([side + ": " +
                          ", ".join(what
                                    for what, where in self.positions.items()
                                    if where == side)
                          for side in ("left", "right")])

    def __hash__(self):
        """ Returns a unique integer computed from the current state.
        """
        return "".join(self.positions.values()).__hash__()

    def all_across(self):
        """ Returns True when all actors have crossed to the right, or False
            otherwise.
        """
        return "left" not in self.positions.values()

    def copy(self):
        """ Returns a new state object that is a copy of self.
        """
        new_object = type(self).empty()
        new_object.positions = self.positions.copy()
        return new_object

    # operators

    @searchtoy.action
    def cross(self):
        """ A state action that causes the farmer to cross the river alone.
        """
        self.positions["farmer"] = self.reverse[self.positions["farmer"]]

    @searchtoy.operator
    def carry(self, what):
        """ A state operator that causes the farmer to cross the river
            carrying one of the three other actors.

            Arguments:
                what: what the farmer carries across with him.
        """
        self.positions[what] = self.positions["farmer"] = self.reverse[self.positions["farmer"]]

    # generator-related methods

    def is_valid(self):
        """ Checks if a state is valid and returns True or False.

            In this case, a problem state is valid when the sheep is not left
            with the sheep or the cabbage.
        """
        return not (self.positions["wolf"] == self.positions["sheep"] != self.positions["farmer"] or
                    self.positions["sheep"] == self.positions["cabbage"] != self.positions["farmer"])

    def operations(self):
        """ Yields the operations that can be performed on a state.

            In this case, operations involve either the farmer crossing the
            river alone, or carrying any actor on the same side with him.

            Since this is an incosistent generator, there is no consideration
            of 'legality' on the generated states. This is taken care of by the
            is_valid() method.
        """
        yield self.operators.cross()
        for what in ("wolf", "cabbage", "sheep"):
            if self.positions[what] == self.positions["farmer"]:
                yield self.operators.carry(what)


# command-line arguments
parser = argparse.ArgumentParser(description="Solves the wolf, cabbage and goat problem.")

# generic
parser.add_argument('--method', choices=searchtoy.blind_methods,
                    default='DepthFirst',
                    help='the search method to be used')

settings = parser.parse_args()

# problem and method
crossing = searchtoy.Problem(crossState(), crossState.all_across)
method = getattr(searchtoy, settings.method)()

# single solution
solution = crossing.optimal(method)
for operation in solution.path.operations:
    print(operation)
print(solution.state)
print("explored", method.nb_explored, "states")
