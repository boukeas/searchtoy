# The Wolf, the Cabbage and the Goat

(description from Algorithmic Puzzles, by Anany and Maria Levitin)

A man finds himself on a riverbank with a wolf, a goat, and a head of
cabbage. He needs to transport all three to the other side of the river in
his boat. However, the boat has room for only the man himself and one
other item (either the wolf, the goat, or the cabbage). In his absence, the
wolf would eat the goat, and the goat would eat the cabbage. Show how
the man can get all these "passengers" to the other side.

## Characteristics

- Generator: are there different ways to generate the successor states? No.
  There is a single generator embedded in the state representation. The search
  space is a _graph_.
- Evaluation: is a heuristic function available for evaluating nodes and
  guiding the search? No, the search is _blind_.
- Cost: is there a cost function that needs to be minimized? **Yes**, the cost
  associated with a solution is its _depth_.
- Solution path: The solution required is the _path_ to the goal state.

## Usage

For help on command-line parameters, use the `-h` switch.

    python3 examples/river-crossing/river.py -h

Solve the problem:

    python3 examples/bridge-crossing/bridge.py
