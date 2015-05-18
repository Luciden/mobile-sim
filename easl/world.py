__author__ = 'Dennis'

from log import Log


class Sensor(object):
    def __init__(self):
        """
        Attributes
        ----------
        observations
            Reference to the observations list of the Entity with this Sensor.
        signals : {name: [value]}
        :return:
        """
        self.observations = None
        self.signals = {}
        self.default_signals = {}

        self.init()

    def init(self):
        """
        Used to specify the signals and signal values that this Sensor can
        sense.
        """
        raise NotImplementedError()

    def set_observations(self, observations):
        """
        Args:
            observations: a dictionary that the Sensor can use to put interpreted
                observations in.
        """
        self.observations = observations

    def detects_modality(self, modality):
        return False


class Signal(object):
    def __init__(self, modality, sig_type, value, values):
        """
        Attributes
        ----------
        modality : string
            Describes the modality that this signal is in.
        type : string
            An abstract description of what this signal represents.
        value : value
            The value associated with the type
        values : []
            All possible values this signal can have.
        """
        self.modality = modality
        self.sig_type = sig_type
        self.value = value
        self.values = values


class World(object):
    """
    Handles and arranges Entities and handles interactions between any
    observable event and its observer(s).

    Describing a World consists of describing the Entities in it and the
    relations between those Entities.

    Part is based on the RegionalSenseManager from "Artificial Intelligence for
    Games" while ignoring some parts as the representation used in this simulation
    is a kind of 'distanceless' representation.
    In other words, only the essentials.

    Differences with RegionalSenseManager:
     * no distances.
     * no notification queue, since all notifications are handled immediately.
     * signals are added in the beginning phase of a frame and sent at the end
       phase, which means all signals can be sent when all entities have been
       processed.

    Attributes
    ----------
    entities : {name: Entity}
        all entities in the world identified by name
    signals : [(Sensor, Signal)]
        All queued signals with their destinations.
    actions
    triggers : [(Entity, Entity, string)]
        the connections between entities that link actions and triggers
    time
    log
    """
    def __init__(self):
        self.entities = {}

        self.signals = []
        self.actions = []

        self.triggers = []

        self.time = 0

        self.log = None

    def run(self, iterations=10):
        """
        Runs the simulation once with the currently specified Entities
        and relations between them.
        """
        self.log = Log()
        self.log.set_verbose()

        # Initialize initial states of all entities, including agents
        for e in self.entities:
            self.entities[e].set_log(self.log)
            self.entities[e].start()

        for i in range(iterations):
            self.time = i
            self.log.time_tick(i)

            self.__do_physics()
            self.__trigger_events()

            self.__queue_signals()
            self.__send_signals()

            self.__queue_actions()
            self.__execute_actions()

            self.__measure_entities()

    def add_entity(self, entity):
        self.entities[entity.name] = entity

    def set_area_of_effect(self, causing, attribute, event, affected):
        """

        Parameters
        ----------
        causing : string
            Name of the Entity that caused the event.
        attribute : string
            Name of the attribute of the Entity that caused the event.
        event : string
            Name of the type of event that occurred.
        affected : string
            Name of the Entity that is affected by the event.
        """
        self.triggers.append((causing, attribute, event, affected))

    def __do_physics(self):
        """
        Calls all Entities' physics method.
        """
        for entity in self.entities:
            self.entities[entity].physics(self.entities[entity])

    def __queue_signals(self):
        """
        Takes all signals that were queued to be emitted and sends queues them
        to be sent to the appropriate receivers.
        """
        for sender in self.entities:
            # First see if it still emits more signals.
            self.entities[sender].emit_signals()

            for signal in self.entities[sender].get_queued_signals():
                for receiver in self.entities:
                    for sensor in self.entities[receiver].sensors:
                        if sensor.detects_modality(signal.modality):
                            self.signals.append((receiver, signal))

    def __send_signals(self):
        while len(self.signals) > 0:
            receiver, signal = self.signals.pop(0)

            self.entities[receiver].add_observation({signal.sig_type: signal.value})

    def __queue_actions(self):
        """
        Makes all Entities prepare their actions.

        The querying and execution phase of the actions should be separated,
        because actions have effects on the Entities' attributes and all
        actions should be selected at the same point in time.
        """
        # Collect the actions by all entities and put them in one list

        for entity in self.entities:
            self.entities[entity].queue_actions()

    def __execute_actions(self):
        """
        Executes all actions
        """
        for entity in self.entities:
            self.entities[entity].execute_actions()

    def __trigger_events(self):
        for cause in self.entities:
            while len(self.entities[cause].event_queue) > 0:
                attribute, event, params = self.entities[cause].event_queue.pop(0)

                # Find all entities that are triggered by this event
                for (causer, causer_attribute, caused_event, affected) in self.triggers:
                    if causer == cause and causer_attribute == attribute and caused_event == event:
                        self.entities[affected].call_trigger(event, params)

    def __measure_entities(self):
        """
        Logs all entities' attributes to be used for analysis.
        """
        for entity in self.entities:
            self.entities[entity].measure()
