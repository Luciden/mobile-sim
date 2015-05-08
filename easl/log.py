__author__ = 'Dennis'

import csv


class Log(object):
    """
    Simple log that contains all experiment information (actions, observations).

    Time based. Logs for every time step what happened.

    Can (not yet) be read from/to files etc.
    """
    def __init__(self, fname=None):
        self.log = []
        self.verbose = False

        if fname is not None:
            self.__from_file(fname)

    def set_verbose(self):
        self.verbose = True

    def add_entry(self, time, kind, data):
        self.log.append([time, kind, data])

    def write_file(self, name):
        f = open(name, 'wt')
        try:
            writer = csv.writer(f)
            for entry in self.log:
                writer.writerow(entry)
        finally:
            f.close()

    def __from_file(self, name):
        f = open(name, 'rt')
        try:
            reader = csv.reader(f)
            for row in reader:
                self.log.append(tuple(row))
        finally:
            f.close()
