# Bridge-Crossing at Night

(description from Algorithmic Puzzles, by Anany and Maria Levitin)

Four people need to cross a rickety footbridge; they all begin on the same
side. It is dark, and they have one flashlight. A maximum of two people
can cross the bridge at one time. Any party that crosses, either one or two
people, must have the flashlight with them. The flashlight must be walked
back and forth; it cannot be thrown, for example. Person 1 takes 1 minute
to cross the bridge, person 2 takes 2 minutes, person 3 takes 5 minutes,
and person 4 takes 10 minutes. A pair must walk together at the rate of the
slower person’s pace. For example, if person 1 and person 4 walk together,
it will take them 10 minutes to get to the other side. If person 4 returns the
flashlight, a total of 20 minutes have passed. Can they cross the bridge in
17 minutes?

## Characteristics

- Generator: are there different ways to generate the successor states? *Yes*,
  solo crossings could be favoured over paired crossings, or vice versa, or
  some combination depending on direction. This affects the number of nodes
  examined, even in such a small problem.
- Evaluation: is a heuristic function available for evaluating nodes and
  guiding the search? No, the search is _blind_.
- Cost: is there a cost function that needs to be minimized? *Yes*, it is the
  _total amount of time_ required for all persons to cross the bridge.
- Solution path: The solution required is the _path_ to the goal state.
