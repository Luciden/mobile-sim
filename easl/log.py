__author__ = 'Dennis'

import csv


class Log(object):
    """
    Simple log that contains all experiment information (actions, observations).

    Time based. Logs for every time step what happened.

    Can (not yet) be read from/to files etc.
    """
    def __init__(self):
        """
        Attributes
        ----------
        log : [{}]
            All entries.
            An entry describes time, type of entry and its type-related data.
        verbose : bool
            If set to True, logging attempts are printed to stdout.
        """
        self.log = []
        self.verbose = False

        self.time = 0

    def read_file(self, file_name):
        """
        Parameters
        ----------
        file_name : string
            Name of the file to read the log from.
        """
        self.__from_file(file_name)

    def set_verbose(self, verbose=True):
        self.verbose = verbose

    def time_tick(self, time=None):
        if time is None:
            self.time += 1
        else:
            self.time = time

        if self.verbose:
            print "t {0}".format(self.time)

    def do_log(self, kind, data):
        entry = [self.time, kind]

        for k, v in data.items():
            entry.extend([k, v])

        self.log.append(entry)
        print entry

    def write_file(self, name):
        """
        Writes all entries to a file.

        Parameters
        ----------
        name : string
            Name of the file to write to.
        """
        f = open(name, 'wt')
        try:
            writer = csv.writer(f)
            for entry in self.log:
                writer.writerow(entry)
        finally:
            f.close()

    def __from_file(self, name):
        """
        Reads all entries from a file.

        Parameters
        ----------
        name : string
            Name of the file to read from.
        """
        f = open(name, 'rt')
        try:
            reader = csv.reader(f)
            for row in reader:
                self.log.append(tuple(row))
        finally:
            f.close()
