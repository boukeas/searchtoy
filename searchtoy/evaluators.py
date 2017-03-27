### evaluators.py: heuristic state evaluation

from abc import abstractmethod

from .exceptions import EvaluatorError

__all__ =  ['Evaluator', 'RandomEvaluator', 'evaluator']


class EvaluatorMeta(type):
    """ A metaclass for creating Evaluator classes.

        The metaclass ensures that Evaluator instances cannot be created and
        it checks that:

        > the 'evaluate' method of a (derived) Evaluator class is static
        > the 'order' method of a (derived) Evaluator class is a class method

        If any of these conditions are not met, an EvaluatorError exception
        is raised.
    """

    def __init__(cls, name, bases, namespace):
        super().__init__(name, bases, namespace)
        if 'evaluate' in namespace and not isinstance(namespace['evaluate'], staticmethod):
            raise EvaluatorError(cls.__name__, "evaluate", "static")
        if 'order' in namespace and not isinstance(namespace['order'], classmethod):
            raise EvaluatorError(cls.__name__, "order", "class")

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

    @staticmethod
    @abstractmethod
    def evaluate(node):
        """ Evaluates a search node and returns its value.
        """
        return NotImplementedError

    @classmethod
    def order(cls, nodes):
        """ Sorts a list of nodes in descending order, using the evaluation
            function as a sorting key.
        """
        nodes.sort(key = cls.evaluate)


class RandomEvaluator(Evaluator):
    """ An Evaluator that shuffles the nodes in random order.
    """

    import random

    @classmethod
    def order(cls, nodes):
        cls.random.shuffle(nodes)


def evaluator(function):
    """ A function decorator that creates a subclass of the Evaluator
        class out of a function that is capable of evaluating nodes.

        Usage:

            @evaluator
            def heuristic(node):
                ...

            # uses the heuristic *class* for node evaluation during search
            method = DepthFirst(evaluator=heuristic)

    """
    return EvaluatorMeta(function.__name__, (Evaluator,), {'evaluate': staticmethod(function)})
