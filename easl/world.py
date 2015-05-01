__author__ = 'Dennis'


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


class SightSensor(Sensor):
    def detects_modality(self, modality):
        return modality == "sight"

    def notify(self, signal):
        if signal.type == "movement":
            self.observations["movement"] = True


class HearingSensor(Sensor):
    def detects_modality(self, modality):
        return modality == "hearing"


class Signal(object):
    def __init__(self, modality=None, type=None, value=None):
        """
        Attributes:
            modality: string describing the modality that this signal is for
            type: string describing the type of signal this is; an abstract
                description
            value: any value associated with the signal
        """
        self.modality = modality
        self.type = type
        self.value = value


class Notification(object):
    def __init__(self, sensor, signal):
        self.sensor = sensor
        self.signal = signal


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

    Attributes:
        entities:
    """
    def __init__(self):
        self.entities = {}

        self.notifications = []

    def run(self, iterations=10):
        """
        Runs the simulation once with the currently specified Entities
        and relations between them.
        """
        for i in range(iterations):
            """
            self.sense_all()
            actions = self.query_actions()
            self.do_actions(actions)
            """
            print "step " + str(i)
            self.do_physics()
            self.emit_signals()
            self.print_state()

    def print_state(self):
        # Show all individual entity's state
        for entity in self.entities:
            print entity
            print self.entities[entity].print_state()

    def add_entity(self, name, entity):
        # TODO(Dennis): Check for already existing entities.
        self.entities[name] = entity

    def couple_sense(self, sensing, sense, sensed, attribute):
        # TODO(Dennis): Implement.
        pass

    def couple_action(self, actor, action, acted, trigger):
        # TODO(Dennis): Implement.
        pass

    def do_physics(self):
        """
        Makes all Entities advance a time step.
        """
        # Execute the physics rules for every entity
        for entity in self.entities:
            self.entities[entity].step()

    def emit_signals(self):
        for entity in self.entities:
            signals = self.entities[entity].emit_signals()
            for signal in signals:
                print "emitting: " + signal.type
                self.add_signal(signal)

        self.send_signals()

    def sense_all(self):
        """
        Passes sense information on to all Entities.
        """
        # TODO(Dennis): Implement.
        # Update all sensors

        pass

    def query_actions(self):
        """
        Collects which actions the Entities want to perform.

        Returns:
            a list of agent/actions pairs that should be executed.
        """
        # Collect the actions by all entities and put them in one list
        actions = []
        for entity in self.entities:
            actions += entity.act()

        return actions

    def do_actions(self, actions):
        """
        Executes all actions, triggering appropriate Triggers.
        """
        # TODO(Dennis): Implement.
        pass

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
