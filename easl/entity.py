__author__ = 'Dennis'

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
        physics: a function that changes the state using only the state's
            attributes
        emission: a function that returns a list of signals to be emitted
            in this frame, based on the Entity's internal state.
    """
    def __init__(self):
        self.attributes = {}
        self.a = self.attributes
        self.sensors = []
        self.observations = {}
        self.physics = lambda self: None
        self.emission = lambda self: []

    def step(self):
        self.physics(self)

    def add_sensor(self, sensor):
        sensor.set_observations(self.observations)
        self.sensors.append(sensor)

    def emit_signals(self):
        return self.emission(self)

    def set_emission(self, emission):
        self.emission = emission

    def add_action(self, name, params):
        # TODO(Dennis): Implement.
        pass

    def set_physics(self, physics):
        self.physics = physics

    def add_attribute(self, name, value):
        self.attributes[name] = value

    def add_trigger(self, name, params):
        # TODO(Dennis): Implement.
        pass

    def print_state(self):
        for a in self.attributes:
            print a + ": " +  str(self.attributes[a])
        for obs in self.observations:
            print obs + ": " + str(self.observations[obs])
        print "\n"
