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

        # {name: []}
        self.parameter_order = {}
        # {name: name}
        self.parameter_last = {}
        for variable in self.variables:
            self.parameter_order[variable] = []
            self.parameter_order[variable] = [par for par in self.variables[variable].keys()]
            self.parameter_last[variable] = self.parameter_order[variable].pop()

        self.table = self.__make_table_rec(self.order, None)
        print self.table

    def __make_table_rec(self, order, p_order):
        """
        Parameters
        ----------
        p_order : [name]
            Set to the list of orders for the current variable.
        """
        # make the full joint of the provided variables by making a tree of
        # variable name/value dicts and storing the probabilities at the end.
        # When a new variable was chosen and we have to get the parameter order
        if p_order is None:
            # When we are not yet at the last variable
            if len(order) > 0:
                # Take the parameter order of the next variable
                p_order = self.parameter_order[order[0]]
            # When we are at the last variable
            else:
                # Take the parameter order of the last variable
                p_order = self.parameter_order[self.last]

        if len(order) == 0:
            # If at the last parameter of the last variable
            if len(p_order) == 0:
                # Create the holders for the counts for all parameter values
                counts = {}

                # For all values of this last parameter
                for value in self.variables[self.last][self.parameter_last[self.last]]:
                    counts[value] = 0

                return counts
            # If this is not yet the last parameter
            else:
                current = {}

                for value in self.variables[self.last][p_order[0]]:
                    current[value] = self.__make_table_rec(order, p_order[1:])

                return current
        # When there is still variables to expand
        else:
            if len(p_order) == 0:
                current = {}

                for value in self.variables[order[0]][self.parameter_last[order[0]]]:
                    # Expand the next variable and choose the appropriate p_order
                    current[value] = self.__make_table_rec(order[1:], None)

                return current
            # Still parameters to expand
            else:
                current = {}

                for value in self.variables[order[0]][p_order[0]]:
                    current[value] = self.__make_table_rec(order, p_order[1:])

                return current

    def set_value(self, vals, value):
        """
        Parameters
        ----------
        vals : {name: {name: value}}
        value : value
        """
        current = self.table

        for name in self.order:
            for param in self.parameter_order[name]:
                current = current[vals[name][param]]
            current = current[vals[name][self.parameter_last[name]]]

        for param in self.parameter_order[self.last]:
            current = current[vals[self.last][param]]

        current[vals[self.last][self.parameter_last[self.last]]] = value

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

        # Go through the variables
        for name in self.order:
            for param in self.parameter_order[name]:
                current = current[vals[name][param]]
            # Take the last parameter into account for every variable
            current = current[vals[name][self.parameter_last[name]]]

        # Go through the last variable's parameters
        for param in self.parameter_order[self.last]:
            current = current[vals[self.last][param]]

        current[vals[self.last][self.parameter_last[self.last]]] += 1

    def get_value(self, vals):
        current = self.table

        for name in self.order:
            for param in self.parameter_order[name]:
                current = current[vals[name][param]]
            current = current[vals[name][self.parameter_last[name]]]

        for param in self.parameter_order[self.last]:
            current = current[vals[self.last][param]]

        return current[vals[self.last][self.parameter_last[self.last]]]

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
