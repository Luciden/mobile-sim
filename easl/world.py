__author__ = 'Dennis'

class World(object):
    """
    Handles and arranges Entities.

    Describing a World consists of describing the Entities in it and the
    relations between those Entities.
    """
    def __init__(self):
        self.entities = []

    def run(self):
        """
        Runs the simulation once with the currently specified Entities
        and relations between them.
        """
        # TODO(Dennis): Implement.
        self.do_physics()
        self.sense_all()
        actions = self.query_actions()
        self.do_actions(actions)

    def add_entity(self, entity):
        # TODO(Dennis): Check for already existing entities.
        self.entities.append(entity)

    def couple_sense(self, sensing, sense, sensed, attribute):
        # TODO(Dennis): Implement.
        pass

    def couple_action(self, actor, action, acted, trigger):
        # TODO(Dennis): Implement.
        pass

    def sense_all(self):
        """
        Passes sense information on to all Entities.
        """
        # TODO(Dennis): Implement.
        pass

    def do_physics(self):
        """
        Makes all Entities advance a time step.
        """
        # TODO(Dennis): Implement.
        pass

    def query_actions(self):
        """
        Collects which actions the Entities want to perform.

        Returns:
            a list of agent/actions pairs that should be executed.
        """
        # TODO(Dennis): Implement.
        pass

    def do_actions(self, actions):
        """
        Executes all actions, triggering appropriate Triggers.
        """
        # TODO(Dennis): Implement.
        pass
