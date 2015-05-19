__author__ = 'Dennis'

from controller import Controller


class LogController(Controller):
    def __init__(self, original, log):
        """
        Attributes
        ----------
        log : Log
            Log from which to play back.
        time : int
            Time step of the log that we're at now.
        original : string
            Name of the original entity.
        watched : {name: (name, function)}
            All measured attributes that are watched.
            For every attribute, store the name of the action that should be
            called here, and a function that calculates the value for the
            action of the form f(old, new): value.
        links : {name: name}
            Map from names in the original entity to names in this entity.
        previous : {name: value}
            For every attribute in links, have the value that it was at last time.
        """
        super(LogController, self).__init__()

        self.actions = {}
        self.log = log
        self.time = 0
        self.watched = {}
        self.links = {}
        self.original = original

        self.next = []

    def init_internal(self, entity):
        self.actions = entity.actions
        self.time = 0
        self.next = self.log.get_at_time(self.time + 1)

    def set_link(self, link):
        self.links.update(link)

    def set_watched(self, attribute, action, function):
        self.watched[attribute] = (action, function)

    def sense(self, observation):
        # Not necessary since this Agent only acts.
        pass

    def act(self):
        """
        Returns
        -------
        """
        # Read the log for the current time step
        now = self.next
        self.next = self.log.get_at_time(self.time)

        actions = []

        # See if the watched value was changed
        for e in now:
            if e["_type"] == "measurement" and e["entity"] == self.original:
                # Find the watched attributes
                # See how it changes in the next step and calculate which
                # action should be performed.
                for f in self.next:
                    if f["_type"] == "measurement" and f["entity"] == self.original:
                        # For watched variables, calculate change
                        for w in self.watched:
                            actions.append((self.watched[w][0], self.watched[w][1](e[w], f[w])))

        return actions
