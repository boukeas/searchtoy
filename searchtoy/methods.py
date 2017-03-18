### methods.py: generic search method and derived concrete search methods

from abc import ABC

from .containers import Stack, OrderedStack, Queue, OrderedQueue, PriorityQueue
from .space import Node
from .exceptions import GeneratorError

methods = ['DepthFirst', 'BreadthFirst', 'BestFirst']
blind_methods = ['DepthFirst', 'BreadthFirst']

__all__ = methods + ['methods', 'blind_methods']


class Method(ABC):
    """ Generic class for traversing a problem's search space.

        The implementation of a search method typically requires the use of a
        container, to store the states of the search space that are to be
        explored. During the search for a solution, states are removed from
        the container, examined and expanded.

        Different search methods use different containers with different
        characteristics.
    """

    def __init__(self, container):
        self.container = container        

    def search(self, problem, lower_bound=None, upper_bound=None):
        """ Systematically searches for a solution in a problem's state space.

            The implementation is based on three enhanced generator functions
            (coroutines) that are chained together and exchange nodes and 
            information about these nodes. This results in a clean, modular
            design, where each coroutine handles a specific task and coroutines
            can be interchanged, depending on the characteristics of the
            problem or the method at hand.

            See PEP 342: Coroutines via Enhanced Generators at
            https://www.python.org/dev/peps/pep-0342/.

            Attributes:
                problem: the problem instance to be solved (contains the start
                    state and a function for checking candidate solutions)
                lower_bound: the lowest possible cost for a solution (the
                    search stops if a solution with this cost is obtained)
                upper_bound: the greatest acceptable cost for a solution (all
                    states with a greater cost are not explored further)
        """

        # [replaced] due to the counter decorator 
        # self.nb_explored = self.nb_solutions = 0

        @counter('nb_explored', self)
        def node_manager(container):
            """ Coroutine for handling node storage and retrieval.

                Arguments:
                    container: the container to be used for storing the nodes
                        in the search frontier.

                Yields: a node removed from the frontier
                Receives: the successor nodes of the yielded node, to be added
                    to the frontier
            """
            nb_explored = 0
            while container:
        
                # [replaced] due to the counter decorator 
                # self.nb_explored += 1
                nb_explored += 1
                print(nb_explored, end = "\r")

                successors = yield container.remove()
                if successors is not None:
                    container.extend(successors)

        def successor_manager(generator, next):
            """ Coroutine for handling node expansion.

                Arguments:
                    generator: a Generator object for expanding nodes
                    next: the coroutine that handles node storage and retrieval

                Yields: nodes to be checked as expandable
                Receives: a boolean indicating whether each node should be
                    expanded into its successor nodes

                Yielded to (from next): nodes to be processed
                Sends (to next): a list of each node's successors
            """
            current = next.send(None)
            while True:
                # yields current node and receives whether it is expandable
                if (yield current):
                    successors = list(generator.successors(current))
                else:
                    successors = None

                try:
                    current = next.send(successors)
                except StopIteration:
                    break

        def conditional_successor_manager(generator, next):
            """ Coroutine for handling node expansion (in graph search spaces)

                The function maintains a dict of the states it has encountered
                before, along with their costs. When a node is expanded, only
                unvisited nodes are forwarded to the node handling coroutine,
                or previously visited nodes for which a less costly path has
                now been discovered.

                Arguments:
                    generator: a Generator object for expanding nodes
                    next: the coroutine that handles node storage and retrieval

                Yields: nodes to be checked as expandable
                Receives: a boolean indicating whether each node should be
                    expanded into its successor nodes

                Yielded to (from next): nodes to be processed
                Sends (to next): a list of each node's successors
            """
            current = next.send(None)
            explored = {}

            while True:

                # yields current node and in notified whether it is expandable
                if (yield current):

                    successors = []
                    for successor in generator.successors(current):

                        # if state already visited, retrieve cost of past visit
                        cost = explored.get(successor.state)

                        if cost is None:
                            # state hasn't been explored before
                            explored[successor.state] = successor.cost
                            successors.append(successor)
                        elif successor.cost < cost:
                            # state has been explored before, at a higher cost
                            explored[successor.state] = successor.cost
                            successors.append(successor)
                else:
                    successors = None

                try:
                    current = next.send(successors)
                except StopIteration:
                    break

        @counter('nb_solutions', self)
        def solution_manager(problem, upper_bound, lower_bound, next):
            """ Coroutine for handling problem solutions.

                Arguments:
                    problem: the problem instance to be solved
                    lower_bound: the lowest possible cost for a solution
                    upper_bound: the greatest acceptable cost for a solution
                    next: the coroutine that handles node expansion

                Yields: solutions to the problem

                Yielded to (from next): nodes to be checked
                Sends (to next): a boolean indicating whether each node should
                    be expanded into its successor nodes
            """
            # initialization of next: produce the first yield
            current = next.send(None)
            while True:
                solution = problem.is_solution(current.state)
                below_upper_bound = upper_bound is None or current.cost < upper_bound

                if solution:
                    # [replaced] due to the counter decorator 
                    # self.nb_solutions += 1
                    yield current

                    # update upper bound
                    if below_upper_bound:
                        upper_bound = current.cost
                    # terminate search if solution cost reached the lower bound
                    if lower_bound is not None and current.cost <= lower_bound:
                        break

                try:
                    current = next.send(not solution and below_upper_bound)
                except StopIteration:
                    break

        # main body of search method

        if problem.start.generator is None:
            raise GeneratorError("A generator has not been attached to the " + problem.start.__class__.__name__ + " class.")

        self.container.insert(Node(problem.start))
        if problem.start.generator.graph:
            # graph search
            return solution_manager(problem, upper_bound, lower_bound,
                   conditional_successor_manager(problem.start.generator,
                   node_manager(self.container)))
        else:
            # tree search
            return solution_manager(problem, upper_bound, lower_bound,
                   successor_manager(problem.start.generator,
                   node_manager(self.container)))


### search methods, derived from Method, using different containers

class DepthFirst(Method):
    """ Depth-first search.

        The container used in depth-first search is a stack. A heuristic
        evaluator may be used for ordering the nodes prior to pushing them
        on the stack.
    """

    def __init__(self, evaluator=None):
        if evaluator is None:
            super().__init__(Stack())
        else:
            super().__init__(OrderedStack(evaluator))


class BreadthFirst(Method):
    """ Breadth-first search.

        The container used in breadth-first search is a Queue. A heuristic
        evaluator may be used for ordering the nodes prior to inserting them
        in the queue.
    """

    def __init__(self, evaluator=None):
        if evaluator is None:
            super().__init__(Queue())
        else:
            super().__init__(OrderedQueue(evaluator))


class BestFirst(Method):
    """ Best-first search.

        The container used in any form of best-first search is a priority queue
        using a heuristic evaluator for ordering the nodes.
    """

    def __init__(self, evaluator):
        super().__init__(PriorityQueue(evaluator))


### aux coroutine (and useful template for decorating generator functions)

def counter(name, obj=None):
    """ A decorator for a generator function, to count #times it has yielded.

        Argument:
            name: the name of the counter attribute
            obj: the object that the counter is attached to, as an attribute
                (if None, it is attached to the decorated function itself)
    """

    def decorator(generator_function):

        nonlocal obj
        if obj is None:
            # default obj: the function returned by the decorator
            obj = replacement

        # counter creation and initialization
        setattr(obj, name, 0)

        def count(generator_object):
            """ A generator function that forwards 'send' and 'yield' calls
                to and from a generator object and counts the number of times
                it yields.

                The counter itself is an attribute of 'obj', which lives in the
                closure.
            """
            # first value yielded by generator_object
            received = generator_object.send(None)
            while True:
                # increase counter
                setattr(obj, name, getattr(obj, name) + 1)
                # yields whatever was yielded from generator_object and
                # receives what was sent to it in response
                sent = yield received
                # forwards what was sent to generator_object and
                # intercepts what was yielded from it
                received = generator_object.send(sent)

        def replacement(*args, **kwargs):
            """ Creates generator_object out of the generator_function and
                wraps it with the 'count' generator function.
            """
            generator_object = generator_function(*args, **kwargs)
            return count(generator_object)

        return replacement

    return decorator




    '''
    # what follows is the "traditional" implementation of search_graph
    # keeping it here for reference

    def search_graph(self, problem, lower_bound=None, upper_bound=None):

        generator = problem.start.generator

        # στατιστικές πληροφορίες για την αναζήτηση
        nb_explored = nb_solutions = 0
        total_time = 0
        timestamp = time.perf_counter()
        #
        frontier = self.container
        # [only for graph search]
        explored = dict()

        # το "μέτωπο" των κόμβων προς εξέταση, περιέχει αρχικά τη ρίζα
        root = Node(problem.start)
        frontier.insert(root)
        explored[root.state] = 0

        # όσο απομένουν κόμβοι προς εξέταση
        while frontier:
            
            # αφαιρείται ο κόμβος στην κορυφή της στοίβας
            current = frontier.remove()
            
            # προσαύξηση του πλήθους των καταστάσεων
            nb_explored += 1
            print(nb_explored, end = "\r")

            # tracing
            total_time += time.perf_counter() - timestamp
            Tracer.trace(point="current state", state=current.state)
            timestamp = time.perf_counter()

            if problem.is_solution(current.state):

                #
                total_time += time.perf_counter() - timestamp
                #
                nb_solutions += 1
                self.nb_explored = nb_explored
                self.nb_solutions = nb_solutions
                self.total_time = total_time
                self.solution_node = current
                #
                yield current
                # 
                if upper_bound is None or current.cost < upper_bound:
                    upper_bound = current.cost
                if lower_bound is not None and current.cost <= lower_bound:
                    break
                timestamp = time.perf_counter()

            # [only for graph search]
            elif upper_bound is None or current.cost < upper_bound:

                successors = []
                # for successor in current.successors():
                for successor in generator.successors(current):

                    # tracing
                    total_time += time.perf_counter() - timestamp
                    Tracer.trace(point="successor state", state=successor.state, cost=successor.cost)
                    timestamp = time.perf_counter()

                    # if state already visited, retrieve cost of past visit
                    cost = explored.get(successor.state)

                    if cost is None:
                        # state hasn't been explored before
                        explored[successor.state] = successor.cost
                        successors.append(successor)
                    elif successor.cost < cost:
                        # state has been explored before, at a higher cost
                        explored[successor.state] = successor.cost
                        successors.append(successor)
                        # tracing
                        Tracer.trace(point="reinsert state", cost=successor.cost)
                    else:
                        # tracing
                        Tracer.trace(point="already explored")

                frontier.extend(successors)
        #        
        total_time += time.perf_counter() - timestamp
    '''


