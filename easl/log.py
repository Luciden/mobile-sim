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
        self.length = 0

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

    def get_length(self):
        return self.length

    def get_at_time(self, time):
        entries = []
        for e in self.log:
            if e["_time"] == time:
                entries.append(e)

        return entries

    def time_tick(self, time=None):
        if time is None:
            self.time += 1
        else:
            self.time = time

        if self.verbose:
            print "t {0}".format(self.time)

    def do_log(self, kind, data):
        entry = {"_time": self.time, "_type": kind}
        entry.update(data)

        self.log.append(entry)
        self.length = self.time
        if self.verbose:
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
            writer = csv.DictWriter(f)
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
            reader = csv.DictReader(f)
            for row in reader:
                self.log.append(row)
        finally:
            f.close()

    def make_kicking_data(self, file):
        """
        Parameters
        ----------
        file : string
            File name to write to.
        """
        f = open(file, "wt")
        try:
            writer = csv.writer(f, delimiter=' ')

            writer.writerow(["t", "n"])
            for entry in self.log:
                if "observation" in entry and entry["observation"] == "movement" and entry["value"] == "faster":
                    writer.writerow([entry["_time"] - 1, str(1)])
        finally:
            f.close()

    @staticmethod
    def make_bins(name, n):
        f = open(name + ".csv", "rt")
        o = open(name + "_bins.csv", "wt")
        try:
            # Skip header
            f.readline()
            reader = csv.reader(f, delimiter=' ')

            bins = []
            bin = 1
            current = 0
            for row in reader:
                if int(row[0]) >= bin * n:
                    bins.append(current)
                    bin += 1
                    current = 0
                current += int(row[1])
            bins.append(current)

            writer = csv.writer(o, delimiter=' ')

            writer.writerow(["block", "n"])
            for i in range(len(bins)):
                writer.writerow([str(i), str(bins[i])])
        finally:
            f.close()
            o.close()
