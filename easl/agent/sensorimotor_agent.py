__author__ = 'Dennis'

from agent import Agent


class SensorimotorLearningAgent(Agent):
    # TODO(Dennis): Implement.
    """
    Uses sensorimotor learning based on the comparator mechanism.

    Needs
     - unknown
    """
    def __init__(self):
        pass

    def init_internal(self, actions):
        raise NotImplementedError("Hmm.")

    def sense(self, observation):
        raise NotImplementedError("Hmm.")

    def act(self):
        raise NotImplementedError("Hmm.")
