__author__ = 'Dennis'

class PhysicalState(object):
    """
    Attributes:
        physics: a function that changes the state using only the state's
            attributes.
    """
    def __init__(self):
        self.physics = lambda: None

class Action(object):
    """
    An Action that
    """
    def __init__(self, name):
        self.name = name
        self.change = lambda self: None

class Entity(object):
    """
    The basic component in the simulation.

    An Entity can perform actions and be acted on itself, and it can observe
    It can observe other Entities.

    An Entity is a self-contained unit and should not have any references
    directly (in its Physical State) to other Entities in a possible World.
    If an Entity has a reference at all, it is one that is in its Internal
    State, grounded in experience through its Senses.

    Attributes:
        physical: a PhysicalState containing the Entity's attribute information.
    """
    def __init__(self):
        self.physical = PhysicalState()
        pass

    def add_action(self, name, params):
        # TODO(Dennis): Implement.
        pass

    def add_attribute(self, name, value):
        # TODO(Dennis): Implement.
        pass

    def add_trigger(self, name, params):
        # TODO(Dennis): Implement.
        pass
