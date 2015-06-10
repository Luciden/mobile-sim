__author__ = 'Dennis'

from controller import Controller
import csv


class FileController(Controller):
    def __init__(self, original, file_name):
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
        super(FileController, self).__init__()

        self.actions = {}
        self.file_name = ""
        self.time = 0
        self.watched = {}
        self.links = {}
        self.original = original
        self.columns = {}
        self.data = {}

        self.next = []

    def init_internal(self, entity):
        self.actions = entity.actions
        self.time = 0

        # Read the file
        f = open(self.file_name + ".csv", "rt")
        try:
            reader = csv.reader(f, delimiter=' ')
            header = reader.next()

            for i in range(len(header)):
                self.columns[i] = header[i]

            for row in reader:
                for i in range(1, len(row)):
                    if row[i] == 1:
                        self.data[row[0]] = self.columns[i]
        finally:
            f.close()

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
        name = self.data[self.time]
        # TODO: make sure doesn't get stuck in up/down position.

        return []
