__author__ = 'Dennis'

from copy import deepcopy
import itertools


class DifferentVariableError(Exception):
    pass


class Table(object):
    def __init__(self, variables):
        self.table = {}
        self.variables = variables

        # Sort the variables so the representation is more predictable
        self.order = list(self.variables.keys())
        self.order.sort()

        self.last = self.order.pop()

    def get_value(self, vals):
        raise NotImplementedError()

    def set_value(self, vals, value):
        raise NotImplementedError()

    def get_variable_values(self, name):
        raise NotImplementedError()


class FullTable(Table):
    def __init__(self, variables):
        """
        Parameters
        ----------
        variables : {name: [value]}

        Attributes
        ----------
        table : {name: {name: ... {name: value} ... }}
        variables : {name: [name]}
        order : [name]
        last : name
        """
        super(FullTable, self).__init__(variables)

        self.table = self.__make_table_rec(self.order)
        print "Made table"

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

    def get_variable_values(self, name):
        return self.variables[name]

    def set_value(self, vals, value):
        """
        Parameters
        ----------
        vals : {name: value}
        value : value
        """
        current = self.table

        for name in self.order:
            if name not in vals:
                raise IndexError("There is no variable {0} in this Table".format(name))
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
        vals : {name: value}
        """
        current = self.table

        for name in self.order:
            current = current[vals[name]]

        return current[vals[self.last]]

    def do_operation(self, f):
        """
        Perform function f(x) on every element.

        Parameters
        ----------
        f : function x: f(x)
        """
        self.__do_operation_rec(f, self.table, self.order)

    def __do_operation_rec(self, f, current, order):
        if len(order) == 0:
            for value in current:
                current[value] = f(current[value])
        else:
            for value in current:
                self.__do_operation_rec(f, current[value], order[1:])


class SparseTable(Table):
    def __init__(self, variables):
        super(SparseTable, self).__init__(variables)
        # Reset the table, make a
        self.table = {}
        self.variables = variables

        self.order = list(self.variables.keys())
        self.order.sort()

        self.last = self.order.pop()

    def get_variables(self):
        return self.variables.copy()

    def get_variable_values(self, name):
        return self.variables[name]

    def __make_entry(self, entry):
        current = self.table

        for name in self.order:
            if entry[name] in current:
                current = current[entry[name]]
                continue
            else:
                current[entry[name]] = {}
                current = current[entry[name]]
                continue

        current = 0

    def set_value(self, vals, value):
        current = self.table

        for name in self.order:
            if vals[name] not in current:
                self.__make_entry(vals)
                # try again, but now the entry exists
                self.set_value(vals, value)
                return

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
            if vals[name] not in current:
                self.__make_entry(vals)
                self.set_value(vals, 1)
                return

            current = current[vals[name]]

        current[vals[self.last]] += 1

    def get_value(self, vals):
        """
        Parameters
        ----------
        vals : {name: value}
        """
        current = self.table

        for name in self.order:
            current = current[vals[name]]

        return current[vals[self.last]]

    def do_operation(self, f):
        """
        Perform function f(x) on every element.

        Parameters
        ----------
        f : function x: f(x)
        """
        self.__do_operation_rec(f, self.table, self.order)

    def __do_operation_rec(self, f, current, order):
        if len(order) == 0:
            for value in current:
                current[value] = f(current[value])
        else:
            for value in current:
                self.__do_operation_rec(f, current[value], order[1:])

    def to_string(self):
        return self.__to_string_rec(self.table, self.order, "")

    def __to_string_rec(self, current, order, so_far):
        s = ""
        if len(order) == 0:
            for value in current:
                s += "{0}, {1}={2}: {3}\n".format(so_far, self.last, value, current[value])
        else:
            for value in current:
                s += self.__to_string_rec(current[value], order[1:], "{2}, {0}={1}".format(order[0], value, so_far))

        return s


class Distribution(SparseTable):
    def __init__(self, variables, freq=None):
        """
        Parameters
        ----------
        {name: [value]}

        Attributes
        ----------
        variables : {name: [value]}
            Variables and for each a list of their possible values.
        """
        if freq is None:
            super(Distribution, self).__init__(variables)
        elif isinstance(freq, SparseTable):
            self.variables = deepcopy(freq.variables)
            self.order = deepcopy(freq.order)
            self.last = deepcopy(freq.last)

            self.table = deepcopy(freq.table)
        else:
            raise RuntimeError("Not a Table.")

    def __eq__(self, other):
        if not isinstance(other, Distribution):
            return False

        # Check if variables and values are the same
        for variable in self.variables:
            if variable not in other.variables:
                return False
            else:
                a = self.variables[variable]
                b = self.variables[variable]

                if not set(a) == set(b):
                    return False

        # Check if all values are the same
        values = []
        for variable in self.order:
            values.append(self.variables[variable])
        values.append(self.variables[self.last])

        for combination in list(itertools.product(*values)):
            vals = {}
            for i in range(len(self.order)):
                vals[self.order[i]] = combination[i]
            vals[self.last] = combination[-1]

            if self.get_value(vals) != other.get_value(vals):
                return False

        return True

    def get_value(self, vals):
        return super(Distribution, self).get_value(vals)

    def set_value(self, vals, value):
        super(Distribution, self).set_value(vals, value)

    def get_variable_values(self, name):
        return super(Distribution, self).get_variable_values(name)

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
        return self.get_value(vals)

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
        return self.partial_prob({variable: value})

    def partial_prob(self, vals):
        # Check if all variables are here
        for variable in vals:
            if variable not in self.order and variable != self.last:
                raise IndexError("Variable {0} is not in this distribution.".format(variable))

        return self.__partial_prob_rec(vals, self.table, self.order)

    def __partial_prob_rec(self, vals, current, order):
        """
        Calculates the probability of a set of variable=value pairs.

        By summing all branches of other variables and then only taking the
        probabilities of the branches that go through the variable=value branch.

        """
        p = 0

        if len(order) > 0:
            # If we found the variable
            if order[0] in vals:
                # Take only the branch with the specified value for that variable
                if vals[order[0]] in current:
                    p += self.__partial_prob_rec(vals, current[vals[order[0]]], order[1:])
                else:
                    return 0.0
            # If the variable is one we do not have a particular value for
            else:
                # Sum the probabilities of all possible values for that variable
                for branch in current:
                    p += self.__partial_prob_rec(vals, current[branch], order[1:])
        # When we're at the end (with the values)
        else:
            # If this is the variable
            if self.last in vals:
                # Only take the number for the value that the variable was set to
                if vals[self.last] in current:
                    p += current[vals[self.last]]
            # If its a different variable
            else:
                # Sum over all the values
                for value in current:
                    p += current[value]

        return p
