__author__ = 'Dennis'


class Controller(object):
    """
    Blah.

    Maybe integrate sense-plan-act into one process?
    (Because all information is already stored in Entity.)

    Need some kind of time representation.
    """
    def __init__(self):
        """
        Attributes
        ----------
        log : Log
        actions : {name: [value]}
            Action symbols and possible values.
        sensory : {name: [value]}
            Sensory symbols and possible values.
        signals : {name: [value]}
            All signals and possible values that can be sensed by the entity.
        default_action : {name: value}
        default_signal : {name: value}
        """
        self.log = None

        self.variables = {}
        self.actions = {}
        self.sensory = {}

        self.signals = {}

        self.default_action = {}
        self.default_signal = {}

    def set_log(self, log):
        self.log = log

    def init_internal(self, entity):
        """
        Called at the beginning of simulation to initialize internal representation.

        Should include a list of all possible actions the controller can do.

        Parameters
        ----------
        entity : Entity
        """
        # Strip the functions from the action predicates
        self.actions = {}
        for action in entity.actions:
            self.actions[action] = entity.actions[action][1]

        signals = {}
        for sensor in entity.sensors:
            signals.update(sensor.signals)

            self.signals.update(sensor.signals)
            self.default_signal.update(sensor.default_signals)

        # Add all together into variables
        self.default_action = entity.default_action

        self.sensory.update(entity.attribute_values)
        self.sensory.update(signals)

        self.variables.update(self.actions)
        self.variables.update(self.sensory)

    def sense(self, observation):
        """
        Receive a part of the observable world.

        Called once for every piece of information in every time step.
        Both information about own body and external world.

        Parameters
        ----------
        observation : {name: value}
            name/value pair of what was observed, which can be processed/stored
            according to the Agent's needs
        """
        raise NotImplementedError("Hmm.")

    def act(self):
        """
        Use current state of the internal model to see which actions should
        be performed.

        Returns
        -------
        []
            All actions that should be performed in this time step.
        """
        raise NotImplementedError("Hmm.")

