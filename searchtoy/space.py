# space.py: contains the necessary components for manipulating the search space
#           (states, generators, nodes, paths, operators and operations).

from abc import abstractmethod
from collections import namedtuple
from copy import deepcopy

from .exceptions import MalformedOperator, GeneratorError

__all__ = ['State', 'ConsistentGenerator', 'InconsistentGenerator', 'Path', 'operator', 'action']


class StateMeta(type):
    """ A metaclass for the State class.

        > It adds an 'operators' namedtuple as a class attribute, which
          contains all the state operators (i.e. all state methods decorated
          with @operator or @action). This comes in handy (syntax-wise) when
          generating successor states.

        > It handles Generator mixins, endowing states with the capability of
          defining their own operations() method and generating successors,
          when there is no need to provide distinct, interchangeable generator
          classes.
    """

    def __new__(cls, clsname, bases, namespace, *, graph=True):
        return super().__new__(cls, clsname, bases, namespace)

    def __init__(cls, clsname, bases, namespace, *, graph=True):
        super().__init__(clsname, bases, namespace)

        # part 1: handle state operators

        # retrieve @operator- or @action-decorated methods from namespace
        operator_mapping = {
            # the attribute name is mapped to an Operator object
            name:getattr(attribute, 'operator')
            # for every attribute (and its name) in the class namespace
            for name, attribute in namespace.items()
            # if the attribute has been marked as an operator of any kind
            if hasattr(attribute, 'operator')}

        # create the cls.operators namedtuple, from the decorated methods
        cls.operators = namedtuple(clsname+'Operators', 
                                   operator_mapping.keys())(**operator_mapping)

        # now, undo the effects of the decoration: state operators should only
        # be accessible through cls.operators
        for attribute in namespace.values():
            if hasattr(attribute, 'operator'):
                delattr(attribute, 'operator')

        # part 2: handle Generator mixins

        # retrieve Generator mixins from bases        
        generator_bases = [generator
                           for generator in bases
                           if issubclass(generator, ConsistentGenerator) or
                              issubclass(generator, InconsistentGenerator)]

        if len(generator_bases) > 1:
            # there are multiple Generator mixins
            raise GeneratorError("Multiple Generator subclasses provided as mixins to the State subclass. " +
                                 "Use either one of ConsistentGenerator or InconsistentGenerator or " + 
                                 "attach a derived Generator to the State.")
        elif len(generator_bases) == 1:
            # this is the Generator mixin
            generator = generator_bases[0]
            if 'operations' not in namespace:
                # the operations() method is not implemented
                raise GeneratorError(generator.__name__ + 
                                     " has been used as a mixin to the " + 
                                     clsname + " class, so " + clsname + 
                                     ".operations() should be implemented.")
            if issubclass(generator, InconsistentGenerator):
                # the is_valid() method is not implemented
                if 'is_valid' not in namespace:
                    raise GeneratorError("InconsistentGenerator " +
                                     "has been used as a mixin to the " + 
                                     clsname + " class, so " + clsname + 
                                     ".is_valid() should be implemented.")

            # error checking complete: the generator mixin is silently attached
            # to the state class
            cls.generator = generator
            cls.generator.graph = graph
            cls.generator.operations = cls.operations
            if issubclass(generator, InconsistentGenerator):
                cls.generator.is_valid = cls.is_valid


class State(metaclass=StateMeta):
    """ A generic State class for representing the state of the search problem.

        Classes derived from State hold all problem-specific information that
        may be relevant during the search, including information required by a
        Generator for generating successor states.

        States are search-method agnostic.

        State objects may freely contain mutable attributes and yet they are
        practically immutable during search: every state (except the initial
        search state), is created by duplicating its parent state and applying
        an operator. Once created in this manner, a state is never again
        altered during search. Immutability is what makes the states hashable.

        For every search problem, you need to:
    
        > Derive from State to create a subclass that holds problem-specific
          state information.
        > For this State subclass, you need to:
            - Implement __str__() and __hash__().
            - Override the copy() method (not necessary but highly advisable).
            - Define methods that modify the state and decorate them with
              @search.operator and @search.action, so that they
              can serve as operators during search.
            - Provide a Generator subclass as a mixin and implement the 
              operations() method OR create one or more distinct Generator
              subclasses and attach them to the state class.
    """

    # A search typically generates many State objects, so __slots__ is used 
    # to conserve memory. Consider using __slots__ in subclasses too.
    __slots__ = ()
    
    # The 'generator' class attribute holds the generator that is attached to
    # the class and will be used to generate successor states during search
    generator = None

    @abstractmethod
    def __str__(self):
        """ Returns a "nicely printable" string representation of the state.

            Needs to be implemented in subclasses of State.
        """
        raise NotImplementedError

    @abstractmethod
    def __hash__(self):
        """ Returns a unique integer computed from the current state.

            Needs to be implemented in subclasses of State.
        """
        return hash(str(self))

    def __eq__(self, other):
        """ Compares two states for equality, based on their hashes.

            You shouldn't override this method.
        """
        return self.__hash__() == other.__hash__()

    @abstractmethod
    def copy(self):
        """ Returns a new state object that is a copy of itself.

            This function is crucial because every state (except the initial
            search state) is created as a copy of its parent state.

            This default implementation will always work but is uses deepcopy,
            which is painfully slow. It is strongly advised that you override
            the default implementation of copy() in State's subclasses.

            Implementation template for copy() in direct subclasses of State:

                def copy(self):
                    new_object = type(self).empty()
                    # ... copy attributes from self into new_object
                    return new_object

            Implementation template for copy() in indirect subclasses of State:

                def copy(self):
                    new_object = super().copy()
                    # ... copy additional attributes from self into new_object
                    return new_object

            Note that this default implementation is intentionally declared as
            an abstract method. Even if it is to be used, it still has to be
            overriden and called explicitly.
        """
        return deepcopy(self)
    
    @classmethod
    def empty(cls):
        """ Factory method that creates and returns a new, uninitialized state
            object. 

            This is to be used in the implementation of the copy() method in
            State subclasses, which will first use empty() to create the new
            object and then initialize it (see copy() documentation).
        """
        return cls.__new__(cls)
    
    # attach is a class method, until we find a reason to attach different
    # generators to different state instances of the same class.
    # Q: should attach belong to State or Generator?
    @classmethod
    def attach(cls, generator):
        """ Attaches a Generator subclass to a State subclass.

            Generators are responsible for generating a state's successors.
            This attachment mechanism allows for different generators to be
            used for the same search problem and the same state representation.

            Each generator has a 'requires' class attribute, that stipulates
            which State subclass the generator can function with. In order for
            an attachment to be successful, the state and the generator must be
            compatible.       
        """
        if cls.generator is not None:
            # there is already a generator
            raise GeneratorError("A " + cls.generator.__name__ +
                                 " has already been attached to " + cls.__name__)
        elif not hasattr(generator, 'requires'):
            # there is no 'requires' attribute in the generator
            raise GeneratorError(generator.__name__ + 
                                 " should have a 'requires' class attribute.")
        elif not issubclass(cls, generator.requires):
            # the generator's 'requires' attribute is incompatible with this class
            raise GeneratorError(generator.__name__ + " can only be attached to (subclasses of) " + 
                                 generator.requires.__name__)
        elif not hasattr(generator, 'graph'):
            # there is no 'graph' attribute in the generator
            raise GeneratorError(generator.__name__ + " should have a boolean 'graph' class attribute.")
        elif getattr(generator, 'graph') not in (True, False):
            # the 'graph' attribute in the generator is not boolean
            raise GeneratorError(generator.__name__ + " should have a boolean 'graph' class attribute.")
        else:
            # error checking done, now attach generator
            cls.generator = generator

        '''
        elif not isinstance(generator.operations, staticmethod):
                # the operations() method is not static
                raise GeneratorError(generator.__name__ + ".operations() should be a @staticmethod.")
        elif issubclass(generator, InconsistentGenerator) and not isinstance(generator.is_valid, staticmethod):
            # the is_valid() method is not static
            raise GeneratorError(generator.__name__ + ".is_valid() should be a @staticmethod.")
        '''

        
class Generator():
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
    
    @staticmethod
    @abstractmethod
    def operations(state):
        """ Yields the operations that can be performed on a state.

            This is a class method so that it can (possibly) use auxillary
            class methods.
        """
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def successors(node):
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
    
    @staticmethod
    @abstractmethod
    def is_valid(self):
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



class Node:
    """ Generic Node class for the nodes of the search space. 

        Each node object contains a state object and additional search-related
        information. Nodes contain absolutely no problem-specific information
        and are also search-method agnostic. This is why there is no need to
        subclass Node for specific problems or search methods.

        Attributes (in slots):
            state: a state of the search space
            parent: the parent of this state
            operation: the operation that lead from the parent to this state
                (including its cost)
            cost: the cumulative cost of reaching this state from the initial
                state
    """

    __slots__ = ('state', 'parent', 'operation', 'cost')

    def __init__(self, state, parent=None, operation=None, cost=0):
        # default arguments correspond to the root node
        self.state = state
        self.parent = parent
        self.operation = operation
        self.cost = cost

    @property
    def path(self):
        """ Returns a Path object that contains the history of states and
            operations that lead to the state in this node. This is typically
            called for solution states.
        """            
        return Path(self)


class Path:
    """ A sequence of states or, equivalently, a sequence of operations.

        Paths are necessary because, in some problems, a solution is not the
        goal state itself but rather the sequence of operations that leads from
        the initial state to the goal state. 

        A path is re-constructed starting from a terminal node (typically a
        goal node) and following the parent links back to the initial node.
        Both the sequence of states and the corresponding sequence of actions
        that transforms each state into the next are available.

        One can iterate over the states, the operations or the Path itself --
        which yields (state, operation) pairs.

        Attributes (in slots):
            states: the sequence of states that comprise the path
            operations: the sequence of actions that comprise the path

# use this to add usage examples

def print_leaf(solution):
    print(solution.state, end="\n\n")

def print_path(solution):
    for state, operation in solution.path:
        print(state, operation, end="\n\n")
    print_solution(solution)

    """

    __slots__ = ("states", "operations")

    def __init__(self, node):
        current = node
        self.states = []
        self.operations = []
        # collect states and operations following the parent links from the node
        # to the root
        while current.parent is not None:
            self.states.append(current.state)
            self.operations.append(current.operation)
            current = current.parent
        # this is the root, append it as well
        self.states.append(current.state)
        # reverse the path so that the root comes first
        self.states = reversed(self.states)
        self.operations = reversed(self.operations)

    def __iter__(self):
        """ Returns an iterator for the (state, operation) pairs in the path.

            The goal state will *not* be yielded by the iterator and you will
            need to handle it separately. This is because the goal state is
            not paired with an operation and excluding it avoids code that
            checks for this special case.
        """
        return zip(self.states, self.operations)


class Operator:
    """ Corresponds to a method that alters a search state.

        Operators typically expect arguments, so they cannot be directly
        applied to states. They first need to be 'called', to be provided with
        specific parameteres. The call returns an Operation, which can actually
        be applied to a state. Applying an Operation to a state returns a new
        modified state, at a cost depending on the Operation's arguments.

        An Operator is created for every state method decorated with @operator.
        
        Operators and Operations are the mechanism by which successor states
        are produced by parent states during search. 
    """

    __slots__ = ('operator')

    def __init__(self, method):
        # the operator needs to 'remember' which method will be called
        # when it is applied
        self.operator = method
        
    def __call__(self, *args, cost=1, **kwargs):
        """ Calls the Operator. 

            The call provides the Operator with specific (positional and
            keyword) arguments, as well as a cost. The call returns an
            Operation which can subsequently be applied to a state.
        """
        return Operation(operator=self.operator, args = args, kwargs = kwargs, cost = cost)


class Operation(namedtuple('OperationBase', ('operator', 'args', 'kwargs', 'cost'))):
    """ Corresponds to an Operator, along with specific arguments and cost.

        A different Operation is created by every call to an Operator, i.e. for
        every pending application of a parametric operator to a state, with
        specific parameters.
        
        Operators and Operations are the mechanism by which successor states
        are produced by parent states during search. Operations can directly
        be applied to states. Applying an Operation on a state returns a new
        modified state.

        It is the operations() method of generators that is responsible for
        yielding the Operations that can be applied to a given state.
    """

    # A search typically generates many Operation objects, so __slots__ is used
    # to conserve memory.
    __slots__ = ()

    def apply(self, state):
        """ Returns a new state on which the Operation has been applied. 
        """
        new_state = state.copy()
        self.operator(new_state, *self.args, **self.kwargs)
        return new_state

    def __str__(self):
        """ Returns a "nicely printable" string representation of the operator.

            Useful for printing the operations in a path.
        """      
        arglist = []
        if self.args:
            arglist.extend([str(value) for value in self.args])
        if self.kwargs:
            arglist.extend([key + "=" + str(value) for key, value in self.kwargs.items()])
        return '[{cost}] {name}({arglist})'.format(
                                                   cost=self.cost,
                                                   name=self.operator.__name__, 
                                                   arglist=', '.join(arglist))


class Action:
    """ Corresponds to a method *without arguments* that alters a search state.

        Actions are a special case of Operators. Since they do not accept
        arguments they can directly be applied to states. Applying an Action
        to a state returns a new modified state, at a fixed cost.

        A single Action is created for every state method decorated with
        @action and are thus "cheaper" than Operations.
        
        As special cases of Operators, Actions are part of the mechanism by
        which successor states are produced by parent states during search.

        The operations() method of generators is responsible for yielding the
        operators and/or actions that can be applied to a given state.
    """ 

    __slots__ = ('operator', 'cost')

    def __init__(self, method, cost):
        # the action needs to 'remember' which method will be called
        # when it is applied, and at what cost
        self.operator = method
        self.cost = cost
        
    def __call__(self):
        """ Calls the Action.

            When called, the Action returns itself (because there are no
            parameters to the operator, it can be directly applied).
        """
        return self

    def __str__(self):
        """ Returns a "nicely printable" string representation of the action.

            Useful for printing the operations in a path.
        """
        return '[{cost}] {name}()'.format(cost=self.cost, name=self.operator.__name__)

    def apply(self, state):
        """ Returns a new state on which the Action has been applied.
        """
        new_state = state.copy()
        self.operator(new_state)
        return new_state


def operator(method):
    """ A decorator that marks state methods as Operators.

        When this decorator is applied to a state method, it adds an 'operator'
        attribute to the method, containing an Operator.

        Usage (inside the definition of a class derived from State):

            @state.operator
            def modify_state(self):
                ...

        In the operations() method of a generator, possible operations on a
        state can be generated using the 'operator' attributes of state methods
        that have been decorated as operators:

            def operations(self, state):
                ...
                yield state.modify_state.operator(arg, kwarg=..., cost=arg)

        Because of the StateMeta metaclass, all methods decorated as operators
        can also be accessed through the state's 'operators' attribute:
            
            def operations(self, state):
                ...
                yield state.operators.modify_state(arg, kwarg=..., cost=arg)
    """
    method.operator = Operator(method)
    return method


def action(*args, **kwargs):
    """ A decorator that marks state methods without arguments as Actions.

        When this decorator is applied to a state method, it adds an 'operator'
        attribute to the method, containing an Action.

        Usage (inside the definition of a class derived from State):

            @state.action               # default cost of applying action is 1
            def modify_state(self):
                ...

            @state.action()             # default cost of applying action is 1
            def modify_state(self):
                ...

            @state.action(cost=2)       # cost of applying operator is 2
            def modify_state(self):
                ...

        In the operations() method of a generator, possible actions on a
        state can be generated using the 'operator' attributes of state methods
        that have been decorated as actions:

            def operations(self, state):
                ...
                yield state.modify_state.operator()

        Because of the StateMeta metaclass, all methods decorated as operators
        can also be accessed through the state's 'operators' attribute:
            
            def operations(self, state):
                ...
                yield state.operators.modify_state()
    """
    if len(args) == 1 and callable(args[0]) and not kwargs:
        # form: @action
        method = args[0]
        method.operator = Action(method, cost=1)
        return method
    elif not args:
        if not kwargs:
            # form: @action()
            cost = 1
        elif len(kwargs) == 1 and 'cost' in kwargs:
            # form: @action(cost=...)
            cost = kwargs['cost']
        else:
            raise MalformedOperator

        def mark(method):
            method.operator = Action(method, cost)
            return method

        return mark
    else:
        raise MalformedOperator

