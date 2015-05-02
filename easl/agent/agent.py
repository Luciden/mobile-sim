__author__ = 'Dennis'


class Agent(object):
    """
    Blah.

    Maybe integrate sense-plan-act into one process?
    (Because all information is already stored in Entity.)

    Need some kind of time representation.
    """
    # TODO(Dennis): Design and implement Agent.
    # TODO(Dennis): How to convert from Entity attributes to internal representation?
    # TODO(Dennis): How to let Agent know which actions can be executed?
    # TODO(Dennis): How to pass actions to Entity?
    def __init__(self):
        pass

    def init_internal(self):
        """
        Called at the beginning of simulation to initialize internal representation.
        """
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

    def do_action(self, name):
        """
        Queues an action to be performed in the Act state.
        """
        # TODO(Dennis): Implement.
        # Check if action exists.
        # Add to actions to be performed.
        pass

