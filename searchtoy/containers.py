### containers.py: generic and concrete containers used in search methods

from abc import ABC, abstractmethod
from collections import deque
from heapq import heappush, heappop, heapify

containers = ['Stack', 'Queue', 'PrioritizedStack', 'PrioritizedQueue', 'PriorityQueue']
__all__ = containers

# cooperative multiple inheritance:
# https://rhettinger.wordpress.com/2011/05/26/super-considered-super/


class Container(ABC):
    """ A abstract base container for the nodes in the search frontier.

        Different search methods use different containers with different
        features for storing the nodes, but all search methods interact with
        their container using the same interface, defined by this class.
    """

    @abstractmethod
    def insert(self, node):
        raise NotImplementedError

    @abstractmethod
    def extend(self, nodes):
        raise NotImplementedError

    @abstractmethod
    def remove(self):
        raise NotImplementedError

    @abstractmethod
    def __len__(self):
        raise NotImplementedError


class Stack(list, Container):
    """ A stack Container for holding the search nodes. 

        Depth-first search uses a stack for holding the search nodes, due to
        its inherrent LIFO processing of elements.
    """

    def __init__(self):
        self.insert = self.append
        self.remove = self.pop
        # could replace the def of extend
        # super_extend = super().extend  
        # self.extend = lambda nodes: super_extend(reversed(nodes))

    def extend(self, nodes):
        super().extend(reversed(nodes))


class Queue(deque, Container):
    """ A queue Container for holding the search nodes. 

        Breadth-first search uses a queue for holding the search nodes, due to
        its inherrent FIFO processing of elements.
    """

    def __init__(self):
        self.insert = self.append
        self.remove = self.popleft

###

class EvaluatedContainer:
    """ Use this as a mixin class, simply to signify that a container requires
        an evaluator.
    """
    pass

class PrioritizedStack(Stack, EvaluatedContainer):
    """ A prioritized stack Container uses an evaluator for sorting nodes
        before pushing them on the top of stack.

        Informed depth-first search uses a prioritized stack in order to
        explore interesting branches earlier in the search.
    """

    def __init__(self, *, evaluator):
        super().__init__()
        self.evaluator = evaluator

    def extend(self, nodes):
        nodes.sort(key=self.evaluator.evaluate)
        super().extend(nodes)


class PrioritizedQueue(Queue, EvaluatedContainer):
    """ An 'ordered' queue Container uses an evaluator for sorting nodes before
        inserting them in the back of the queue.

        Informed bradth-first search uses an 'ordered' queue in order to pursue        
        interesting branches earlier in the search.
    """

    def __init__(self, *, evaluator):
        super().__init__()
        self.evaluator = evaluator

    def extend(self, nodes):
        nodes.sort(key=self.evaluator.evaluate)
        super().extend(nodes)


class PriorityQueue(list, EvaluatedContainer):
    """ A priority queue Container for holding the search nodes. 

        Informed search methods such as best-first search and A* employ a
        priority queue in order to pursue interesting branches as early as
        possible in the search.

        The implementation follows Recipe 1.5 in the Python Cookbook by
        David Beazley and Brian K. Jones, which seems to follow the official
        documentation for the heapq module, suggesting to store "entries as
        3-element lists, including the priority, an entry count, and the task."
        (https://docs.python.org/3.4/library/heapq.html)
    """

    def __init__(self, *, evaluator):
        self.count = 0
        self.evaluator = evaluator
        self.evaluate = evaluator.evaluate
        # the following can be used to replace the def of extend
        # self.remove = lambda: partial(lambda heap: heapq.heappop(heap), self)()[2]

    def insert(self, node):
        self.count += 1
        heappush(self, (self.evaluator.evaluate(node), self.count, node))

    def remove(self):
       return heappop(self)[2]

    def extend(self, nodes):
        newnodes = [(self.evaluator.evaluate(node), count, node)
                    for count, node in enumerate(nodes, start=self.count+1)]
        super().extend(newnodes)
        self.count += len(nodes)
        heapify(self)

