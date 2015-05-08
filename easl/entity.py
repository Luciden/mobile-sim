__author__ = 'Dennis'

from copy import copy


class Entity(object):
    # TODO: Document.
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
    log : Log
    attributes : {name: value}
        physical representation of the Entity
    sensors : [Sensor]
    observations : {name: value}
    physics : function
        a function that changes the state using only the state's
        attributes
    emission : function
        Returns a list of signals to be emitted in this frame, based on the
        Entity's internal state.
    actions : {name: (function, {name: [value]})}
        All possible actions identified by their name, with the function that
        describes how its parameters influence the internal state, and
        parameter names with a list/generator of all possible values.
    events : {name: function(old, new)}
        Specifies for every attribute what events it triggers when it changes.
        The functions return an event.
        An event is a tuple of (name, {name: value}) of event name and its
        parameters name/value pairs.
    triggers : {name: function(self, ...)}
        callback functions that change the attributes when called
    agent : Agent
    action_queue : [(name, {name: value})]
        All action/parameter pairs that are queued to be executed.
        Both name and its parameter name/value pairs are provided.
    """
    def __init__(self, name, agent=None):
        self.log = None
        self.name = name

        self.attributes = {}
        self.a = self.attributes
        self.sensors = []
        self.observations = {}
        self.physics = lambda x: None
        self.emission = lambda x: []

        self.actions = {}

        self.events = {}
        self.triggers = {}

        self.agent = agent
        self.action_queue = []
        self.signal_queue = []
        self.event_queue = []

    def start(self):
        """
        Called when the experiment starts.
        """
        if self.agent is not None:
            self.agent.init_internal(self.actions)

    def try_change(self, attribute, value):
        """
        Checks to see if setting the specified attribute's value is different from the
        current value, sets the attribute and notifies.

        Parameters
        ----------
        attribute : string
        value : value

        Returns
        -------
        bool
            True if the attribute changes, False otherwise
        """
        # The emission function is obscure.
        # When attributes change, the modality these attributes are in should
        # determine whether events/signals are sent or not.
        if self.a[attribute] != value:
            old = self.a[attribute]
            self.a[attribute] = value

            # Call the event for this change
            event = self.events[attribute](old, value)
            self.log.do_log("event", {"name": self.name, "attribute": attribute, "old": old, "new": value})

            if event is not None:
                e, params = event
                self.event_queue.append((attribute, e, params))

            return True
        return False

    def set_log(self, log):
        """
        Parameters
        ----------
        log : Log
            Log to use.
        """
        self.log = log
        if self.agent is not None:
            self.agent.set_log(log)

    def queue_actions(self):
        """
        Queues actions to be executed by consulting associated Agent, if available.

        See Also
        --------
        easl.agent.Agent.act : Functionality delegated to Agent.
        """
        if self.agent is None:
            self.action_queue = []
            return

        # pass all observations to agent and have it convert to internal representation
        for observation in self.observations:
            print "x"
            self.log.do_log("observation",
                            {"entity": self.name, "observation": observation, "value": self.observations[observation]})

            self.agent.sense(observation, self.observations[observation])
        self.observations = {}

        # ask agent to give actions
        self.action_queue = self.agent.act()

    def add_attribute(self, name, initial_value, event):
        """
        Parameters
        ----------
        name : string
            Name to identify the attribute by.
        initial_value : value
            Any value that the attribute is set to when the experiment begins.
        event : function(old, new) : (name, value)
            Function that is called when the attribute changes.
            The function receives the old and new values and should return an
            event, i.e. a name and value pair.
        """
        self.attributes[name] = initial_value
        self.events[name] = event

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

    def add_sensor(self, sensor):
        sensor.set_observations(self.observations)
        self.sensors.append(sensor)

    def add_trigger(self, name, trigger):
        """
        A Trigger changes the Entity's internal state if a match for a
        cause was found.

        """
        self.triggers[name] = trigger

    def set_physics(self, physics):
        self.physics = physics

    def set_agent(self, agent):
        self.agent = agent

    def set_emission(self, emission):
        self.emission = emission

    def execute_actions(self):
        """
        Calls all queued actions and clears the queue.
        """
        while len(self.action_queue) > 0:
            name, parameters = self.action_queue.pop(0)

            self.log.do_log("action", {"entity": self.name, "name": name, "parameters": parameters})

            parameters["self"] = self
            self.actions[name][0](**parameters)

    def emit_signals(self):
        self.signal_queue += self.emission(self)

    def get_queued_signals(self):
        """
        Pass all the queued signals so far and clear the queue.
        """
        signals = self.signal_queue
        self.signal_queue = []

        return signals

    def call_trigger(self, name, params):
        if name in self.triggers:
            self.log.do_log("trigger", {"name": name})

            params["self"] = self
            self.triggers[name](**params)

    def is_active(self):
        """
        If the entity performs any actions, i.e. has an associated agent.
        """
        return self.agent is not None

    def measure(self):
        """
        Log all attribute values.

        Parameters
        ----------
        name : string
            Name to identify the measurement by.
        """
        measurement = copy(self.attributes)
        measurement["entity"] = self.name

        self.log.do_log("measurement", measurement)
