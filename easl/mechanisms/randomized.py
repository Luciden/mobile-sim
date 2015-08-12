__author__ = 'Dennis'

import random

from mechanism import Mechanism


class RandomizedMechanism(Mechanism):
    """
    Agent that performs a single random action at every iteration..
    """
    def __init__(self):
        super(RandomizedMechanism, self).__init__()

        self.actions = {}

    def init_internal(self, entity):
        self.actions = entity.actions

    def sense(self, observation):
        # Not necessary since this Agent only acts.
        pass

    def act(self):
        """

        Returns
        -------
        [(string, {string: value})]
            all action/parameter/value structs that should be performed
        """
        # Select one random action to perform.
        action = random.choice(self.actions.keys())
        value = random.choice(self.actions[action][1])

        return [(action, value)]
