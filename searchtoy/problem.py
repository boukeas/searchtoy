### problem.py: combinatorial search problem and different ways to ask for
###     a solution (get one, get all or optimize).

from .exceptions import NoSolution


class Problem:
    """ The Problem class corresponds to an instance of a search problem.

        To describe a specific problem that you need to solve, all you need
        to do is specify the initial state and a function that checks if a
        particular state constitutes a goal state. The class that the initial
        state belongs to specifies the state representation and its attached
        generator is responsible for generating subsequent search states.
        
        For each problem that you need to solve, it is usually sufficient to
        create a simple instance of the Problem class. You typically don't have
        to subclass the Problem class, unless you need to implement an
        is_solution() method as part of the class.
        
        Given a search method, you can solve the problem (ask for the first
        solution found by the method), perform optimization (ask for the best
        solution, probably within specific bounds) or generate all solutions.

        Attributes:
            start: the initial state of the problem instance
            is_solution: a function that checks if a state is a solution
                to the problem instance
    """

    def __init__(self, start, is_solution = None):
        self.start = start
        if is_solution:
            self.is_solution = is_solution
    
    def is_solution(self, state):
        """ Checks if a state is a solution to the problem instance.
        
            If you provide an 'is_solution' function during instance
            construction (as a parameter), the you don't need to subclass
            Problem or implement this function.
        """
        raise NotImplementedError

    def solutions(self, method, lower_bound=None, upper_bound=None):
        """ Returns a generator that yields all the solutions to the problem
            instance.

            Arguments:
                method: the method used to search for solutions
                lower bound: the lowest possible cost for a solution (the
                    search stops if a solution with this cost is obtained)
                upper bound: the greatest acceptable cost for a solution (all
                    states with a greater cost are not explored further)
        """
        return method.search(self, lower_bound, upper_bound)

    def solve(self, method, upper_bound=None):
        """ Returns a single solution to the problem instance, the first one
            to be found.

            Arguments:
                method: the method used to search for solutions
                upper bound: the greatest acceptable cost for a solution
        """
        try:
            return next(self.solutions(method, upper_bound))
        except StopIteration:
            raise NoSolution(self)

    def optimize(self, method, lower_bound=None, upper_bound=None):
        """ Returns a single solution to the problem instance, the best one
            to be found.

            Arguments:
                method: the method used to search for solutions
                lower bound: the lowest possible cost for a solution (the
                    search stops if a solution with this cost is obtained)
                upper bound: the greatest acceptable cost for a solution (all
                    states with a greater cost are not explored further)
        """
        best_solution = None
        for solution in self.solutions(method, lower_bound, upper_bound):
            best_solution = solution
        if best_solution is None:
            raise NoSolution(self)
        return best_solution

