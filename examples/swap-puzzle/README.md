# The Swap Puzzle

(The description is adapted from an [excellent unplugged activity](https://teachinglondoncomputing.org/resources/inspiring-unplugged-classroom-activities/the-swap-puzzle-activity/), although many online versions of the puzzle are also available.)

The puzzle board is a linear array of 2*N + 1 squares. Start the game with N red
pieces at one end of the board and N blue pieces at the other, with each square
occupied by a single piece. The square in the middle should be the only square
left empty at the start.

Here's an example of the initial configuration, on a board with 7 squares,
with 3 red pieces (denoted 'x') and 3 blue pieces (denoted 'o'):

    [ x | x | x |   | o | o | o ]

The aim of the game is to swap the position of the blue pieces with those of the
red pieces. You must do it in as few moves as possible.

There are two kinds of move:
1. Move a piece to an adjacent empty square (forwards or backwards).
1. Jump a single adjacent piece of any color into an empty space (forwards or backwards).

Here's an example of the final configuration, on a board with 7 squares:

    [ o | o | o |   | x | x | x ]

## Characteristics

- Generator: are there different ways to generate the successor states? **Yes**,
  depending on the order in which different operators are tried (this only makes
  sense for _blind_ methods). The search space is a _graph_.
- Evaluation: is a heuristic function available for evaluating nodes and
  guiding the search? **Yes**, a _distance_ metric measures a node's distance
  from the goal. _Informed_ search methods can also be used.
- Cost: is there a cost function that needs to be minimized? **Yes**, the cost
  associated with a solution is its _depth_.
- Solution path: The solution required is the _path_ to the goal state.
