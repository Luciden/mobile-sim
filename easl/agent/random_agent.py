__author__ = 'Dennis'

import random

from agent import Agent


class RandomAgent(Agent):
    """
    Agent that performs random actions.

    FOR DEVELOPMENT PURPOSES ONLY.
    """
    def __init__(self):
        super(RandomAgent, self).__init__()

        self.actions = {}

    def init_internal(self, actions):
        self.actions = actions

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
        parameters = self.actions[action][1]
        # Select a random value for every parameter
        params = {}
        for p in parameters:
            params[p] = random.choice(parameters[p])

        print action, params
        return [(action, params)]
