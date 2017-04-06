# Sudoku

Fill the squares of a 9x9 board with numbers 1-9, so that no two rows, columns
or 3x3 blocks contain the same number twice.

## Characteristics

- Generator: are there different ways to generate the successor states? **Yes**,
  depending on the order in which the board's rows are selected for placing a
  queen. The next available row can simply be selected at each step. In this
  case, the search space is a _tree_.
  Alternatively, row _domains_ can be
  maintained and the most constrained row (the one with the smallest domain) can
  be selected at each step. In this case, the search space is a _graph_.
- Evaluation: is a heuristic function available for evaluating nodes and
  guiding the search? No, the search is _blind_.
- Cost: is there a cost function that needs to be minimized? No, the only cost
  associated with a solution is its _depth_ and all solutions are to be found
  at the same depth.
- Solution path: The solution required is the simply a goal state, _not_ the
  path leading to it.

## Instances

In the ``instances/`` sub-directory, there are about 100 test puzzles taken from
http://norvig.com/sudoku.html, which is generally a very interesting read on
the subject.

## Usage

For help on command-line parameters, use the `-h` switch.

    python3 examples/sudoku/sudoku.py -h

Solves the infamous 'hardest' sudoku by Arto Inkala, using a generator that
branches on the next most constrained square.

    python3 examples/sudoku/sudoku.py -f examples/sudoku/instances/sudoku.inkala --most-constrained
