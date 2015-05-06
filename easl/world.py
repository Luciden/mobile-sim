__author__ = 'Dennis'

import csv


class Sensor(object):
    def __init__(self):
        self.observations = None

    def set_observations(self, observations):
        """
        Args:
            observations: a dictionary that the Sensor can use to put interpreted
                observations in.
        """
        self.observations = observations

    def detects_modality(self, modality):
        return False

    def notify(self, signal):
        pass


class Signal(object):
    def __init__(self, modality=None, sig_type=None, value=None):
        """
        Attributes:
            modality: string describing the modality that this signal is for
            type: string describing the type of signal this is; an abstract
                description
            value: any value associated with the signal
        """
        self.modality = modality
        self.sig_type = sig_type
        self.value = value


class Notification(object):
    def __init__(self, sensor, signal):
        self.sensor = sensor
        self.signal = signal


class Log(object):
    """
    Simple log that contains all experiment information (actions, observations).

    Time based. Logs for every time step what happened.

    Can (not yet) be read from/to files etc.
    """
    # TODO: How to get information from Agent? Make local Log?
    def __init__(self, fname=None):
        self.log = []
        self.verbose = False

        if fname is not None:
            self.__from_file(fname)

    def set_verbose(self):
        self.verbose = True

    def add_entry(self, time, kind, data):
        self.log.append([time, kind, data])

    def write_file(self, name):
        f = open(name, 'wt')
        try:
            writer = csv.writer(f)
            for entry in self.log:
                writer.writerow(entry)
        finally:
            f.close()

    def __from_file(self, name):
        f = open(name, 'rt')
        try:
            reader = csv.reader(f)
            for row in reader:
                self.log.append(tuple(row))
        finally:
            f.close()


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
    notifications
    actions
    triggers : [(Entity, Entity, string)]
        the connections between entities that link actions and triggers
    time
    log
    """
    def __init__(self):
        self.entities = {}

        self.notifications = []
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
            self.entities[e].start()

        for i in range(iterations):
            self.time = i

            print "step " + str(i)
            self.do_physics()
            self.emit_signals()
            self.query_actions()
            self.execute_actions()
            self.trigger_events()

            self.print_state()

        self.log.write_file("log.csv")

    def add_entity(self, name, entity):
        self.entities[name] = entity

    def set_in_area_of_effect(self, affected, event, area):
        """
        Setting the area of effect of an entity's change in attribute
        means that the affected entity's triggers are triggered when the
        attribute changes.

        This can be used to model position etc.

        Parameters
        ----------
        affected : string
            name of the entity that is to be triggered by the action
        event : string
            name of the type of event
        area : string
            identifier of the area that is affected
        """
        self.area_of_effect.append((affected, event, area))

    def set_area_of_effect(self, entity, action, event, area):
        """

        Parameters
        ----------

        """
        # TODO: Implement.
        pass

    def do_physics(self):
        """
        Calls all Entities' physics method.
        """
        for entity in self.entities:
            self.entities[entity].physics()

    def emit_signals(self):
        for entity in self.entities:
            signals = self.entities[entity].emit_signals()
            for signal in signals:
                print "emitting: " + signal.sig_type
                self.add_signal(signal)

        self.send_signals()

    def query_actions(self):
        """
        Makes all Entities prepare their actions.

        The querying and execution phase of the actions should be separated,
        because actions have effects on the Entities' attributes and all
        actions should be selected at the same point in time.
        """
        # Collect the actions by all entities and put them in one list

        for entity in self.entities:
            self.entities[entity].queue_actions()

    def execute_actions(self):
        """
        Executes all actions
        """
        for entity in self.entities:
            entity.execute_actions()

    def add_signal(self, signal):
        # Go through all the sensors to find observers
        for entity in self.entities:
            for sensor in self.entities[entity].sensors:
                # Should be able to sense the modality
                if not sensor.detects_modality(signal.modality):
                    continue

                notification = Notification(sensor, signal)

                self.notifications.append(notification)

    def send_signals(self):
        while len(self.notifications) > 0:
            n = self.notifications.pop(0)
            n.sensor.notify(n.signal)

    def trigger_events(self):
        for cause in self.entities:
            while len(self.entities[cause].events) > 0:
                attribute, value = self.entities[cause].events.pop(0)

                # Find all entities that are triggered by this event
                for (e, c, a) in self.triggers:
                    if c == cause and attribute == a:
                        self.entities[e].try_trigger(attribute, value)

    def print_state(self):
        # Show all individual entity's state
        for entity in self.entities:
            print entity
            print self.entities[entity].print_state()