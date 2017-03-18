### exceptions.py: base exception and derived classes


class Error(Exception):
    """ Base Error exception for the search module.
    """
    pass

class GeneratorError(Error):
    """ A GeneratorError is raised when a Generator subclass is not properly
        created, or when an attempt is made to instantiate a Generator.
    """
    pass

class MalformedOperator(Error):
    """ The MalformedOperator exception is raised when the operator decorator
        is not used properly
    """

    def __str__(self):
        return "Use @operator, @operator() or @operator(cost=...) forms"

class NoSolution(Error):
    """ The NoSolution exception is raised when a problem has no solutions.
    """

    def __str__(self):
        return "There are no solutions to the problem."

class EvaluatorError(Error):
    """ An EvaluatorError is raised when an Evaluator subclass is not properly
        created, or when an attempt is made to instantiate an Evaluator.
    """
    pass

