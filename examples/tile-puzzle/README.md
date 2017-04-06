# The Sliding Tiles Puzzle

(Description adapted from Algorithmic Puzzles, by Anany and Maria Levitin)

This famous puzzle consists of n×n square tiles numbered from 1 to (n×n)-1
which are placed in a n×n box, leaving one square empty. The goal is to
reposition the tiles from a given starting arrangement by sliding them one at
a time into the configuration in which the tiles are ordered sequentially.

Example of initial and target arrangements for the 8-puzzle (3x3):

    initial        target
    -------        -------
    2  8  3        1  2  3
    7  1  5        4  5  6
    .  6  4        7  8  .

## Characteristics

- Generator: are there different ways to generate the successor states? No.
  There is a single generator embedded in the state representation. The search
  space is a _graph_.
- Evaluation: is a heuristic function available for evaluating nodes and
  guiding the search? **Yes**, the well-known _manhattan distance_.
  _Informed_ search methods can also be used.
- Cost: is there a cost function that needs to be minimized? **Yes**, the cost
  associated with a solution is its _depth_.
- Solution path: The solution required is the _path_ to the goal state.

## Instances

In the ``instances/`` sub-directory, you will find files with test instances,
i.e. starting positions for the puzzle.

## Usage

For help on command-line parameters, use the `-h` switch.

    python3 examples/swap-puzzle/swap.py -h

Obtain an optimal solution, using one of the available generators.

Obtain the first solution to a particular instance, using best-first search and
the manhattan distance heuristic.

    python3 examples/tile-puzzle/tiles.py --method BestFirst -f examples/tile-puzzle/instances/tilepuzzle.3
