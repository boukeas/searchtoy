# searchtoy

The `searchtoy` is a python 3 library for solving combinatorial search problems.

It is currenty under development and its interface _is not completely stable_.

The `searchtoy` originated as a personal project, with an intent to experiment
with the characteristics of the python language while building a library that
could actually do something useful. Therefore the library can be used for solving practical combinatorial search problems, while its code can also act as a showcase for several python idioms such as _generators_, _decorators_ and
_metaclasses_.

The `searchtoy` code is licensed under the
[MIT License](https://github.com/boukeas/sherlock/blob/master/LICENSE).

The code in this repository includes many [well-documented examples](https://github.com/boukeas/searchtoy/tree/master/examples) of using
the library to solve typical combinatorial search problems. You can follow
them through to see how you can use the library to solve your own search
problems.

## An overview of the `searchtoy`

### The main classes

#### States

A state is a representation of the current condition of a search problem.

Classes derived from `State` hold all _problem-specific information_ that may be
relevant during the search. This includes information that may be required by a
`Generator` for generating successor states, or by an `Evaluator` for computing
a state's heuristic value.

#### Generators

A generator is responsible for enumerating all the _operations_ that can be
applied to a given search state. It thus determines the _successor states_
(or _descendants_) of a given search state.

Classes derived from `Generator` rely on the problem-specific information
stored in `State`s in order to generate all applicable operations.

In problems where there is only a single obvious way to generate successor
states
(such as the [knight's tour](https://github.com/boukeas/searchtoy/tree/master/examples/knight-tour) or
the [sliding tile puzzle](https://github.com/boukeas/searchtoy/tree/master/examples/tile-puzzle)),
the `Generator` functionality can be embedded in `State`, as a mixin.
In other cases, different `Generator`s can be attached to a `State` and be used
interchangeably.

#### Evaluators

An evaluation function assigns a _heuristic_ value to each state, which is an
estimate of the cost required to reach a solution from that state.

Classes derived from `Evaluator` rely on the problem-specific information
stored in `State`s in order to evaluate them. The values computed by
`Evaluator`s are used by _informed_ search methods in order to guide the search
towards the most promising parts of the search space.

#### Problems

All you need in order to define a particular `Problem` instance is an initial
starting state and a predicate function to recognize goal states.

#### Methods

A search method is a systematic procedure for generating and exploring the states
in a problem's search space, while searching for solutions.

The `searchtoy` provides a generic search `Method` with various different
components. Well-known _blind_ and _informed_ search methods provided
by the library are assembled from the different available components of this
generic search method. Programmatically, this is one of the most interesting
aspects of the library.

### How to use `searchtoy` to solve a problem

When presented with a combinatorial search problem you need to solve with the
`searchtoy`, these are the steps involved:

1. Encapsulate the state representation in a class derived from `State`. Note
   that this also requires that you:
    - Implement the `__str__` and `__hash__` methods for the class.
    - Override the `copy()` method (which is not necessary but highly advisable).
    - Define the methods that modify the state and _decorate_ them with
     `@searchtoy.operator` or `@search.action`, so that they
     can serve as operators during search.

1. - If there is only a single obvious way to generate successor states _for
      a particular state representation_, then
      use either `ConsistentGenerator` or `InconsistentGenerator` as _mixins_
      to the `State` subclass and implement the `operations` generator method.
  - If there are alternative ways to generate successor states _for
      a particular state representation_, then derive
      from `ConsistentGenerator` or `InconsistentGenerator` and implement
      the `operations` generator method for each one of the alternatives.
  - Different generators may `require` different state representations. Also,
      some generators may induce a search space that is _tree-structured_.
1. - Optionally, you can derive from the `Evaluator` class and implement one or
    more heuristic evaluation functions. This will allow you to employ
    _informed_ search methods.
  - Different evaluators may `require` different state representations.
1. Define the `Problem`'s initial state and goal predicate function.
1. Invoke a search method and search for solutions!

## How to install `searchtoy`

Start by cloning this [github repository](https://github.com/boukeas/searchtoy.git) or
simply download the [.zip file](https://github.com/boukeas/searchtoy/archive/master.zip)
and extract it.

``cd`` into the directory containing ``searchtoy``'s code and install it.

    pip install .

If you like, you can install ``searchtoy`` in a virtual environment. Before installing,
create and activate the environment:

    virtualenv ~/environments/searchtoy
    source ~/environments/searchtoy/bin/activate

Here, ``~/environments/searchtoy`` is the directory where the virtual environment
will be installed. You can modify this as you please. Play around and, when you 're
done, deactivate the virtual environment.

    deactivate

The library will eventually be made available through the Python Package Index.
