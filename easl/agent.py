__author__ = 'Dennis'


class Agent(object):
    """
    Blah.

    Maybe integrate sense-plan-act into one process?
    (Because all information is already stored in Entity.)
    """
    # TODO(Dennis): Design and implement Agent.
    # TODO(Dennis): How to convert from Entity attributes to internal representation?
    # TODO(Dennis): How to let Agent know which actions can be executed?
    # TODO(Dennis): How to pass actions to Entity?
    def __init__(self):
        pass

    def act(self):
        """
        Use current state of the internal model to see which actions should
        be performed.

        Returns
        -------
        list
            All actions that should be performed in this time step.
        """
        # TODO(Dennis): Implement.
        return []

    def sense(self, observation):
        """
        Receive a part of the observable world.

        Called once for every piece of information in every time step.
        Both information about own body and external world.
        """
        # TODO(Dennis): Implement.
        pass

    def plan(self):
        """
        Use the sensed information to update internal model.
        """
        # TODO(Dennis): Implement.
        pass


class CausalReasoningAgent(Agent):
    # TODO(Dennis): Implement.
    """
    Uses Causal Bayes Nets based learning.

    Needs
     - conversion of observations to Variables
     - actions as interventions

    Notes
    -----
    Based on work by Gopnik [1]_ and dissertation [2]_.

    References
    ----------
    .. [1] "Thing by Gopnik," Gopnik et al.
    .. [2] Dissertation
    """
    def __init__(self):
        pass


class OperantConditioningAgent(Agent):
    # TODO(Dennis): Implement.
    """
    Uses operant conditioning based learning.

    Needs
     - representation of observations as predicates in memory
     - link between action predicates and actual actions
    """
    def __init__(self):
        pass


class SensorimotorLearningAgent(Agent):
    # TODO(Dennis): Implement.
    """
    Uses sensorimotor learning based on the comparator model.

    Needs
     - unknown
    """
    def __init__(self):
        pass
