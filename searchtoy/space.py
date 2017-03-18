### space.py: elementary components of the search space (states, nodes, paths,
###     operators and operations).

from abc import abstractmethod
from collections import namedtuple
from copy import deepcopy

from .exceptions import MalformedOperator

__all__ = ['State', 'Path', 'operator', 'action']

class StateMeta(type):
    """ A metaclass for the State class.

        This metaclass adds an 'operators' namedtuple as a State class
        attribute, which contains all the operators for the state 
        (i.e. operators corresponding to all the state methods decorated with
        @operator or @action).
    """

    def __init__(cls, clsname, bases, clsdict):
        super().__init__(clsname, bases, clsdict)
        operator_mapping = {
            # the attribute name is mapped to an Operator object
            name:getattr(attribute, 'operator')
            # for every attribute (and its name) in the class namespace
            for name, attribute in clsdict.items()
            # if the attribute has been marked as an operator of any kind
            if hasattr(attribute, 'operator')}

        cls.operators = namedtuple(clsname+'Operators', operator_mapping.keys())(**operator_mapping)

        # now, undo the effects of the decoration: state operators should only
        # be accessible through cls.operators
        for attribute in clsdict.values():
            if hasattr(attribute, 'operator'):
                delattr(attribute, 'operator')


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
            - Attach an appropriate Generator subclass.
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
            raise Exception("A " + cls.generator.__name__ + " has already been attached to " + cls.__name__)
        elif not issubclass(cls, generator.requires):
            raise Exception("A " + generator.__name__ + " can only be attached to (subclasses of) " + generator.requires.__name__)
        else:
            cls.generator = generator


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

