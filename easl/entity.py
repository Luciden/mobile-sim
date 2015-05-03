__author__ = 'Dennis'

from copy import deepcopy


class Entity(object):
    """
    The basic component in the simulation.

    An Entity can perform actions and be acted on itself, and it can observe
    It can observe other Entities.

    An Entity is a self-contained unit and should not have any references
    directly (in its Physical State) to other Entities in a possible World.
    If an Entity has a reference at all, it is one that is in its Internal
    State, grounded in experience through its Senses.

    Actions are local to Entities: They change their internal (physical)
    state.
    The consequences of this, among with the consequences of the entity's
    physics, are used to have interactions between Entities.

    Attributes
    ----------
    physics : function
        a function that changes the state using only the state's
        attributes
    emission : function
        returns a list of signals to be emitted
        in this frame, based on the Entity's internal state.
    """
    def __init__(self, agent=None):
        self.attributes = {}
        self.a = self.attributes
        self.sensors = []
        self.observations = {}
        self.physics = lambda x: None
        self.emission = lambda x: []

        self.actions = {}
        self.events = []
        self.triggers = {}

        self.agent = agent

    def start(self):
        if self.agent is not None:
            self.agent.init_internal(deepcopy(self.actions))

    def step(self):
        self.physics(self)

    def try_action(self, attribute, value):
        if self.a[attribute] != value:
            self.a[attribute] = value
            self.events.append((attribute, value))

            return True
        return False

    def prepare_actions(self):
        """
        X


        Returns:
        [(string, {string: value})]
            all action/parameter/value structs that should be performed

        See Also
        --------
        easl.agent.Agent.act : Functionality delegated to Agent.
        """
        if self.agent is None:
            return []

        # pass all observations to agent and have it convert to internal representation
        for observation in self.observations:
            self.agent.sense(observation)
        self.observations = {}

        # ask agent to give actions
        return self.agent.act()

    def add_action(self, name, parameters, f):
        """
        Adds an action to the possible actions.

        Defining Actions:
            name, [{paramname: [values]}], function

        Parameters
        ----------
        name : string
            name the action will be identified/called by
        parameters : {string: [values]}
            pairs of parameter names and respective possible values
        f : function
            callback that is called for an entity when the action is performed
        """
        self.actions[name] = (f, parameters)

    def do_action(self, name, parameters):
        """

        Sending Actions:
            name, {paramname: value}

        Parameters
        ----------
        name : string
            name of the action
        parameters : {string: string}
            parameter name/value pairs
        """
        print parameters
        parameters["self"] = self
        self.actions[name][0](**parameters)

    def add_sensor(self, sensor):
        sensor.set_observations(self.observations)
        self.sensors.append(sensor)

    def emit_signals(self):
        return self.emission(self)

    def set_emission(self, emission):
        self.emission = emission

    def add_trigger(self, name, trigger):
        """
        A Trigger changes the Entity's internal state if a match for a
        cause was found.
        """
        self.triggers[name] = trigger

    def call_trigger(self, name, params):
        self.triggers[name](**params)

    def try_trigger(self, attribute, value):
        for trigger in self.triggers:
            self.call_trigger(trigger, {attribute: value})

    def set_physics(self, physics):
        self.physics = physics

    def set_agent(self, agent):
        self.agent = agent

    def is_active(self):
        """
        If the entity performs any actions, i.e. has an associated agent.
        """
        return self.agent is not None

    def add_attribute(self, name, value):
        self.attributes[name] = value

    def print_state(self):
        for attr in self.attributes:
            print attr + ": " + str(self.attributes[attr])
        for obs in self.observations:
            print obs + ": " + str(self.observations[obs])
        print "\n"
