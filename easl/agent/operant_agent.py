__author__ = 'Dennis'

from agent import Agent


class OperantConditioningAgent(Agent):
    # TODO(Dennis): Implement.
    """
    Uses operant conditioning based learning.

    Needs
     - representation of observations as predicates in memory
     - link between action predicates and actual actions
    """

    _PREV = -1
    _NOW = 0
    _FUT = 1

    def __init__(self):
        super(OperantConditioningAgent, self).__init__()

        self.memory_size = 8
        self.memory = []

        self.reinforcers = []

    def init_internal(self):
        # Create action and observable predicates
        # Initialize the conjunctions
        pass

    def sense(self, observation):
        # Turn observation into predicate at this time step
        pass

    def act(self):
        # TODO(Dennis): Implement.
        # Calculate maximum action.
        return super(OperantConditioningAgent, self).act()

    def __age_memory(self):
        """
        Updates all memory units' age by one time step.
        """
        for m in range(len(self.memory)):
            if self.memory[m][1] >= self._max_age:
                del self.memory[m]
            else:
                self.memory[m][1] += 1


