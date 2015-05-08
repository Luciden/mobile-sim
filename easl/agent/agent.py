__author__ = 'Dennis'


class Agent(object):
    """
    Blah.

    Maybe integrate sense-plan-act into one process?
    (Because all information is already stored in Entity.)

    Need some kind of time representation.
    """
    def __init__(self):
        self.log = None

    def set_log(self, log):
        self.log = log

    def init_internal(self, actions):
        """
        Called at the beginning of simulation to initialize internal representation.

        Should include a list of all possible actions the agent can do.

        Parameters
        ----------
        actions : {string:[]}
            lists the possible actions and respective possible parameters
        """
        raise NotImplementedError("Hmm.")

    def sense(self, observation):
        """
        Receive a part of the observable world.

        Called once for every piece of information in every time step.
        Both information about own body and external world.

        Parameters
        ----------
        observation : (string, value)
            name/value pair of what was observed, which can be processed/stored
            according to the Agent's needs
        """
        raise NotImplementedError("Hmm.")

    def act(self):
        """
        Use current state of the internal model to see which actions should
        be performed.

        Returns
        -------
        list
            All actions that should be performed in this time step.
        """
        raise NotImplementedError("Hmm.")

