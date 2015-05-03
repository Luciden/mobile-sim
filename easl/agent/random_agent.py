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
        # Store the actions
        self.actions = actions

    def sense(self, observation):
        # Not necessary since this Agent only acts.
        pass

    def act(self):
        # Select one random action to perform.
        k = self.actions.keys()
        i = random.randint(0, k)

        # Select the parameter for the action
        a = self.actions[i]
        j = random.randint(0, len(a))

        return [(k[i], a[j])]
