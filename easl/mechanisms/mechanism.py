__author__ = 'Dennis'

import itertools


class Mechanism(object):
    """ Abstract class for a (learning) mechanism to be used in the simulator.

    All mechanisms have a set of motor signals that can be sent, with the
    respective domains.

    Attributes
    ----------
    log : Log
    all_variables_and_domains : {str: [str]}
    motor_signals_and_domains : {str: [str]}
        Motor signal names and their possible values. Subset of all variables.
    sensory_variables_and_domains : {name: [value]}
        Sensory symbols and possible values. Subset of all variables.
    signals : {name: [value]}
        All signals and possible values that can be sensed by the entity.
    default_action : {name: value}
    default_signal : {name: value}
    """
    def __init__(self, visual=None):
        self.log = None
        self.visual = visual

        self.all_variables_and_domains = {}
        self.motor_signals_and_domains = {}
        self.sensory_variables_and_domains = {}

        self.signals = {}

        self.default_action = {}
        self.default_signal = {}

    def set_log(self, log):
        self.log = log

    def init_internal(self, entity):
        """
        Called at the beginning of simulation to initialize internal representation.

        Should include a list of all possible actions the mechanisms can do.

        Parameters
        ----------
        entity : Entity
        """
        # Strip the functions from the action predicates
        self.motor_signals_and_domains = {}
        for action in entity.actions:
            self.motor_signals_and_domains[action] = entity.actions[action][1]

        signals = {}
        for sensor in entity.sensors:
            signals.update(sensor.signals)

            self.signals.update(sensor.signals)
            self.default_signal.update(sensor.default_signals)

        # Add all together into variables
        self.default_action = entity.default_action

        self.sensory_variables_and_domains.update(entity.attribute_values)
        self.sensory_variables_and_domains.update(signals)

        self.all_variables_and_domains.update(self.motor_signals_and_domains)
        self.all_variables_and_domains.update(self.sensory_variables_and_domains)

    def sense(self, observation):
        """
        Receive a part of the observable world.

        Called once for every piece of information in every time step.
        Both information about own body and external world.

        Parameters
        ----------
        observation : (name, value)
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

    def visualize(self):
        """
        Creates a Visualization from the attributes.
        :return:
        """
        if self.visual is not None:
            return self.visual.visualize(self)
        else:
            return None

    @staticmethod
    def all_possibilities(actions):
        """
        Parameters
        ----------
        actions : {string: [string]}
        """
        return [dict(zip(actions, product)) for product in itertools.product(*(actions[name] for name in actions))]
