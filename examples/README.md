# Examples

In the ``examples/`` directory, you can find quite a few well-known puzzles that
are formulated as combinatorial search problems and solved using ``searchtoy``.

The different examples can be categorized, based on the following
characteristics:

- **Generator**: In some problems, there is a single obvious way to apply
  operators to a search state and generate its successor states. In other
  problems, there are multiple acceptable alternatives (often depending on
  different state representations).

- **Search Space**: A problem's search space can either be a _tree_ or a _graph_.
  The states of a problem's search space form a graph when there is no unique
  way to reach a state and there are multiple paths available to reach it.
  In some cases, the structure of the induced search space _depends_ on the way
  successor states are generated.

- **Evaluator**: In some problems, we can devise a _heuristic_ evaluation
  function that assigns a value to each search state. The states encountered
  during search can be _ordered_ according to these evaluations and search
  can thus be _guided_ towards the most promising parts of the search space.
  Search methods that make use of evaluation functions are _informed_, in
  contrast to _blind_ methods.

- **Optimization**: We are often faced with problems where we do not simply
  seek for _any_ solution, but we are rather interested in solutions that
  _optimize_ a certain well-defined criterion. The simplest and most frequent
  examples are problems where we seek to minimize solution _depth_, that is
  we seek the solutions reached in the smallest number of operations.

Here is a concise table of the example problems that are included, along with
their elementary characteristics as combinatorial optimization search problems:

Example                   | Generator   | Search Space | Evaluator | Optimize
---                       | ---         | ---          |  ---      | ---
Wolf, Cabbage and Goat    | Single      | Graph   | No  | Depth  
Water buckets             | Single      | Graph   | No  | Depth
Knight's tour             | Single      | Graph   | Yes | No
Sliding tile puzzle       | Single      | Graph   | Yes | Depth
Bridge-crossing at night  | Multiple    | Graph   | No  | Cost
N-queens                  | Multiple (r)| Depends | No  | No
Sudoku                    | Multiple    | Depends | No  | No
Swap-puzzle               | Multiple    | Graph   | Yes | Depth

For more information about each problem, check out the individual READMEs.
