__author__ = 'Dennis'

import random

from controller import Controller


class RandomController(Controller):
    """
    Agent that performs random actions.

    FOR DEVELOPMENT PURPOSES ONLY.
    """
    def __init__(self):
        super(RandomController, self).__init__()

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
