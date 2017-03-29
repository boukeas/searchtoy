### evaluators.py: heuristic state evaluation

from abc import abstractmethod
from random import randint

from .exceptions import EvaluatorError

__all__ =  ['Evaluator', 'RandomEvaluator', 'evaluator']


class EvaluatorMeta(type):
    """ A metaclass for creating Evaluator classes.

        The metaclass ensures that Evaluator instances cannot be created and
        it checks that the 'evaluate' method of a (derived) Evaluator class
        is static.

        If these conditions are not met, an EvaluatorError exception is raised.
    """

    def __init__(cls, name, bases, namespace):
        super().__init__(name, bases, namespace)
        if 'evaluate' in namespace and not isinstance(namespace['evaluate'], staticmethod):
            raise EvaluatorError(cls.__name__ + ".evaluate() should be a @staticmethod.")
        if 'requires' not in namespace:
            raise EvaluatorError(cls.__name__ + " should have a 'requires' class attribute.")

    def __call__(self, *args, **kwargs):
        raise EvaluatorError(self.__name__ + " objects cannot be created. Use the class object itself.")


class Evaluator(metaclass=EvaluatorMeta):
    """ Computes heuristic values for the nodes of the search space.

        This is a class (instead of a function) because the user may need
        auxillary functions for evaluating nodes, and it is more elegant to
        group them together as static Evaluator methods.

        An Evaluator (sub-)class object can be passed as a parameter to a
        search method, so that node evaluations can be performed. There is no
        need for creating instances of the class.
    """
    requires = None

    @staticmethod
    @abstractmethod
    def evaluate(node):
        """ Evaluates a search node and returns its value.
        """
        return NotImplementedError

class RandomEvaluator(Evaluator):
    """ An Evaluator that orders the nodes randomly.

        The evaluate() method works by assigning a random positive integer
        no greater than 1000 to each evaluated node.
    """
    requires = None

    @staticmethod
    def evaluate(node):
        return randint(1,1000)


def evaluator(*, requires):
    """ A function decorator that creates a subclass of the Evaluator
        class out of a function that is capable of evaluating nodes.

        Usage:

            @evaluator(requires=<a state representation class>)
            def heuristic(node):
                ...

            # uses the heuristic *class* for node evaluation during search
            method = DepthFirst(evaluator=heuristic)

    """
    def wrapper(function):
        return EvaluatorMeta(function.__name__, (Evaluator,), {'evaluate': staticmethod(function), 'requires': requires})
    return wrapper
