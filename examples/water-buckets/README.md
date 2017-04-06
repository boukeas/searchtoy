# The Water Buckets Problem

(Description is from
[Python for fun](http://www.openbookproject.net/py4fun/buckets/buckets.html)
but many variations can be found with buckets of different sizes
or a different number of buckets, so you may also want to refer to
[Wikipedia](https://en.wikipedia.org/wiki/Liquid_water_pouring_puzzles)).

You go to the well with a 7 liter bucket and an 11 liter bucket. You wish to
fill one of them with exactly X liters of water. How can you do this in the
fewest number of operations, where each operation either fills or empties one
of the two buckets.

## Characteristics

- Generator: are there different ways to generate the successor states? No.
  There is a single generator embedded in the state representation. The search
  space is a _graph_.
- Evaluation: is a heuristic function available for evaluating nodes and
  guiding the search? No, the search is _blind_.
- Cost: is there a cost function that needs to be minimized? **Yes**, the cost
  associated with a solution is its _depth_.
- Solution path: The solution required is the _path_ to the goal state.
