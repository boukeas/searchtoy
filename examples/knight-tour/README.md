# The Knight's Tour

Starting from any initial position, use a knight to visit all the squares of a
chessboard exactly once.

## Characteristics

- Generator: are there different ways to generate the successor states? No.
  There is a single generator embedded in the state representation. The search
  space is a _graph_.
- Evaluation: is a heuristic function available for evaluating nodes and
  guiding the search? **Yes**, in an an _extended_ state representation, an
  accessibility count is maintained for the squares in the board.
  _Informed_ search methods can be used.
- Cost: is there a cost function that needs to be minimized? No, the only cost
  associated with a solution is its _depth_ and all solutions are to be found
  at the same depth.
- Solution path: The solution required is the _path_ to the goal state. However,
  the state representation essentially contains the path, so the goal state is
  sufficient as a solution.
