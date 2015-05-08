__author__ = 'Dennis'

from copy import copy, deepcopy


class Table(object):
    """
    variables : {name: {name: value}}
    """
    # TODO: CHECK IMPLEMENTATION.
    def __init__(self, variables):
        """
        Attributes
        ----------
        table : {name: {name: ... {name: value} ... }}
        variables : {name: {name: [value]}}
        order : [name]
        last : name
        """
        self.table = {}
        self.variables = variables

        self.order = [var for var in self.variables.keys()]
        self.last = self.order.pop()

        self.table = self.__make_table_rec(self.order)
        print self.table

    def __make_table_rec(self, order):
        # TODO: Only actions with a single parameter are taken into account here.
        # To include multiple parameters, have to create orders within variable order.
        # I.e. for every variable determine what the order of parameters is.
        # make the full joint of the provided variables by making a tree of
        # variable name/value dicts and storing the probabilities at the end.
        if len(order) == 0:
            values = {}
            # self.variables[self.last] : {name: [value]}
            names = self.variables[self.last]
            # For every parameter
            for name in names:
                # For every value
                for v in names[name]:
                    # Create a place to store the number
                    values[v] = 0
            return values
        else:
            current = {}

            for value in self.variables[order[0]]:
                current[value] = self.__make_table_rec(order[1:])

            return current

    def set_value(self, vals, value):
        """

        Parameters
        ----------
        vals : dict
            pairs of variable name/value. should contain all variables in the
            distribution.
        p : number
            probability of the situation
        """
        current = self.table
        for name in self.order:
            current = current[vals[name]]

        current[vals[self.last]] = value

    def inc_value(self, vals):
        """
        Parameters
        ----------
        vals :
        """
        # Go down the path taking the turn appropriate for the value in the
        # entry.
        # Then increment.
        current = self.table
        for name in self.order:
            current = current[vals[name]]

        current[vals[self.last]] += 1

    def get_value(self, vals):
        """

        Parameters
        ----------
        vals : dict
            pairs of variable name/value
        """
        current = self.table
        for name in self.order:
            current = current[vals[name]]

        return current[vals[self.last]]

    def do_operation(self, f):
        """
        Perform function f(x) on every element.
        """
        self.__do_operation_rec(f, self.table, self.order)

    def __do_operation_rec(self, f, current, order):
        if len(order) == 0:
            for value in current:
                current[value] = f(current[value])
        else:
            for value in current:
                self.__do_operation_rec(f, current[value], order[1:])


class Distribution(object):
    def __init__(self, variables, freq=None):
        self.table = {}
        self.variables = variables

        if freq is not None:
            self.variables = copy(freq.variables)
            self.order = copy(freq.order)
            self.last = copy(freq.last)

            self.table = deepcopy(freq.table)
        else:
            # get the order of variables, but keep the last one
            # for accessing the probabilities
            self.order = [var for var in self.variables.keys()]
            self.last = self.order.pop()

            self.table = self.__make_table_rec(self.order)

    def __make_table_rec(self, order):
        # make the full joint of the provided variables by making a tree of
        # variable name/value dicts and storing the probabilities at the end.
        if len(order) == 0:
            return dict([(value, 0) for value in self.variables[self.last]])
        else:
            current = {}

            for value in self.variables[order[0]]:
                current[value] = self.__make_table_rec(order[1:])

            return current

    def get_variables(self):
        return self.variables.copy()

    def set_prob(self, vals, p):
        """

        Parameters
        ----------
        vals : dict
            pairs of variable name/value. should contain all variables in the
            distribution.
        p : number
            probability of the situation
        """
        current = self.table
        for name in self.order:
            current = current[vals[name]]

        current[vals[self.last]] = p

    def prob(self, vals):
        """

        Parameters
        ----------
        vals : dict
            pairs of variable name/value
        """
        current = self.table
        for name in self.order:
            current = current[vals[name]]

        return current[vals[self.last]]

    def single_prob(self, variable, value):
        """
        Get the probability for a partial specification with only one variable.

        Parameters
        ----------
        val : (string, string)
            variable name and value pair to check for
        """
        return self.__single_prob_rec(variable, value, self.table, self.order)

    def __single_prob_rec(self, variable, value, current, order):
        p = 0

        # if variable is found, sum all probabilities in branch with appropriate value
        if order[0] == variable:
            p += self.__sum_prob_rec(current[value], order[1:])
        # keep searching for variable and take all branches into account
        else:
            for branch in current:
                p += self.__single_prob_rec(variable, value, current[branch], order[1:])

        return p

    def __sum_prob_rec(self, current, order):
        p = 0
        if len(order) == 0:
            for value in current:
                p += current[value]
        else:
            for value in current:
                p += self.__sum_prob_rec(current[value], order[1:])

        return p
