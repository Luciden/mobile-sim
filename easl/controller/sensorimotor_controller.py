__author__ = 'Dennis'

from controller import Controller


class SensorimotorLearningController(Controller):
    """
    Uses sensorimotor learning based on the comparator mechanism.

    Needs
     - unknown
    """
    def __init__(self):
        pass

    def init_internal(self, entity):
        raise NotImplementedError("Hmm.")

    def sense(self, observation):
        raise NotImplementedError("Hmm.")

    def act(self):
        raise NotImplementedError("Hmm.")
