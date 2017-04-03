# The N-queens problem

The n-Queens Problem Place n queens on an n × n chessboard so that no two queens
attack each other by being in the same column, row, or diagonal.

## Characteristics

- Generator: are there different ways to generate the successor states? **Yes**,
  depending on the order in which the board's rows are selected for placing a
  queen. The next available row can simply be selected at each step. In this
  case, the search space is a _tree_.
  Alternatively, in an an _extended_ state representation, row _domains_ can be
  maintained and the most constrained row (the one with the smallest domain) can
  be selected at each step. In this case, the search space is a _graph_.
- Evaluation: is a heuristic function available for evaluating nodes and
  guiding the search? No, the search is _blind_.
- Cost: is there a cost function that needs to be minimized? No, the only cost
  associated with a solution is its _depth_ and all solutions are to be found
  at the same depth.
- Solution path: The solution required is the simply a goal state, _not_ the
  path leading to it.
