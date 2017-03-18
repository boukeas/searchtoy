### generators.py: generators attached to states produce their successors

from abc import ABCMeta, abstractmethod

from .exceptions import GeneratorError
from .space import State, Node

__all__ = ['ConsistentGenerator', 'InconsistentGenerator']


class GeneratorMeta(ABCMeta):
    """ A metaclass for creating Generator classes.

        The metaclass ensures that Generator instances cannot be created and
        it checks that:

        > all concrete Generator classes have a well-defined 'graph' attribute
        > all concrete Generator classes have a well-defined 'requires' attribute
        > the 'operations', 'successors' and 'is_valid' methods of a (derived)
          Generator class are class methods

        If any of these conditions are not met, a GeneratorError exception
        is raised.
    """

    def __init__(cls, clsname, bases, clsdict):
        super().__init__(clsname, bases, clsdict)
        if not cls.__abstractmethods__ and ('graph' not in clsdict or clsdict['graph'] not in (True, False)):
            raise GeneratorError("The " + clsname + " class should have a 'graph' class attribute, set to either True or False.")
        if not cls.__abstractmethods__ and ('requires' not in clsdict or not issubclass(clsdict['requires'], State)):
            raise GeneratorError("The " + clsname + " class should have a 'requires' class attribute, set to a subclass of State.")
        if 'operations' in clsdict and not isinstance(clsdict['operations'], classmethod):
            raise GeneratorError(clsname + ".operations() should be a class method")
        if 'successors' in clsdict and not isinstance(clsdict['successors'], classmethod):
            raise GeneratorError(clsname + ".successors() should be a class method")
        if 'is_valid' in clsdict and not isinstance(clsdict['is_valid'], classmethod):
            raise GeneratorError(clsname + ".is_valid() should be a class method")

    def __call__(self, *args, **kwargs):
        raise GeneratorError(self.__name__ + " objects cannot be created. Use the class object itself.")


class Generator(metaclass=GeneratorMeta):
    """ Generates all possible operations applicable to a particular state.

        Derived Generator classes will rely on problem-specific information
        stored in search states in order to generate the operations that are
        applicable to a particular state (and thus determine its successors).

        Generators do not store any information themselves, and thus depend
        on the problem-specific information stored in states to perform their
        task. State representations and generators are thus intertwined and
        each generator will *require* that it is attached to particular State
        subclass that contains the problem-specific information it needs.
        
        For most problems there is more than one obvious way to generate
        successor states so, even for the same state representation, different
        generators may be interchangeable.

        Not only can the choice of generator affect search performance, but it
        can even determine whether the search space is a tree or a graph. This
        is why all subclasses of Generator should set the 'graph' attribute to
        either True or False.

        Generators are used as class objects and are not to be instantiated.

        Do not subclass directly from the Generator class. Derive only from
        one of its two sub-classes, depending on the way your Generator works.

        Class attributes:
            - graph: set to either True or False, indicates whether the search
                space is a tree or a graph
            - requires: the State subclass that the generator needs to be
                attached to
    """ 
    
    @classmethod
    @abstractmethod
    def operations(cls, state):
        """ Yields the operations that can be performed on a state.

            This is a class method so that it can (possibly) use auxillary
            class methods.
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def successors(cls, node):
        """ Yields a node's successor nodes.
        """
        raise NotImplementedError


class ConsistentGenerator(Generator):
    """ A ConsistentGenerator yields operations that, when applied to a state, 
        produce successor states that are always valid.

        Subclasses of ConsistentGenerator should not override the successors
        method, but only implement the operations method.
    """

    @classmethod
    def successors(cls, node):
        """ Applies the Generator's operations on the node's state and yields
            all of the node's successor nodes.
        """
        for operation in cls.operations(node.state):
            yield Node(operation.apply(node.state),
                       parent=node,
                       operation=operation,
                       cost=node.cost+operation.cost)


class InconsistentGenerator(Generator):
    """ A InconsistentGenerator yields operations that, when applied to a 
        state, may produce successor states that are not valid. 

        Note that an InconsistentGenerator still only yields *valid* successors
        through the successors() method. It makes use of the is_valid() method
        to prune the invalid ones generated by the operations() method.

        Depending on the problem, it is sometimes more convenient or efficient
        to generate invalid successors and prune them, rather than striving to
        produce only valid successors.

        Subclasses of InconsistentGenerator should not override the
        successors() method, but only implement the operations() and is_valid()
        methods.
    """
    
    @classmethod
    @abstractmethod
    def is_valid(cls, state):
        """ Checks if a state is valid and returns True or False.
        """
        raise NotImplementedError

    @classmethod
    def successors(cls, node):
        """ Applies the generator's operations on the node's state and yields
            the node's valid successor nodes.
        """
        for operation in cls.operations(node.state):
            successor = operation.apply(node.state)
            if cls.is_valid(successor):
                yield Node(successor,
                           parent=node,
                           operation=operation,
                           cost=node.cost+operation.cost)

