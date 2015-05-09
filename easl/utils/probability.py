__author__ = 'Dennis'

from copy import copy, deepcopy


class Table(object):
    # TODO: Revert implementation to consider only 1-parameter variables?
    def __init__(self, variables):
        """
        Parameters
        ----------
        variables : {name: [value]}

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
        """
        Parameters
        ----------
        order : [name]
            Order of the rest of the variables to consider.
        """
        # make the full joint of the provided variables by making a tree of
        # variable name/value dicts and storing the probabilities at the end.
        # When a new variable was chosen and we have to get the parameter order
        if len(order) == 0:
            counts = {}

            for value in self.variables[self.last]:
                counts[value] = 0

            return counts
        else:
            current = {}

            for value in self.variables[order[0]]:
                current[value] = self.__make_table_rec(order[1:])

            return current

    def get_variables(self):
        return self.variables.copy()

    def set_value(self, vals, value):
        """
        Parameters
        ----------
        vals : {name: value}
        value : value
        """
        current = self.table

        for name in self.order:
            current = current[vals[name]]

        current[vals[self.last]] = value

    def inc_value(self, vals):
        """
        Parameters
        ----------
        vals : {name: value}
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
        vals :
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


class Distribution(Table):
    def __init__(self, variables, freq=None):
        if freq is None:
            super(Distribution, self).__init__(variables)
        elif isinstance(freq, Table):
            self.variables = deepcopy(freq.variables)
            self.order = deepcopy(freq.order)
            self.last = deepcopy(freq.last)

            self.table = deepcopy(freq.table)
        else:
            raise RuntimeError("Not a Table.")

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
        self.set_value(vals, p)

    def prob(self, vals):
        """

        Parameters
        ----------
        vals : {name: {name: value}}
        """
        self.get_value(vals)

    def single_prob(self, variable, value):
        """
        Get the probability for a partial specification with only one variable.

        Marginalizing?

        Parameters
        ----------
        variable : string
            Name of variable to get probability for.
        value : string
        """
        return self.__single_prob_rec(variable, value, self.table, self.order)

    def __single_prob_rec(self, variable, value, current, order):
        """
        Calculates the probability of one variable having a certain value.

        By summing all branches of other variables and then only taking the
        probabilities of the branches that go through the variable=value branch.

        """
        p = 0

        if len(order) > 0:
            # If we found the variable
            if order[0] == variable:
                # Take only the branch with the specified value
                p += self.__single_prob_rec(current[value], order[1:])
            # If the variable is a different one
            else:
                # Take all the branches
                for branch in current:
                    p += self.__single_prob_rec(variable, value, current[branch], order[1:])
        else:
            # If this is the variable
            if self.last == variable:
                # Get only the value of the specified variable
                p += current[value]
            # If it is a different one
            else:
                # Sum all possible ones (because we should have passed variable)
                # TODO: Build in a check to see if we passed variable.
                for value in current:
                    p += current[value]

        return p
