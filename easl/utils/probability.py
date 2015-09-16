__author__ = 'Dennis'

from copy import deepcopy
import itertools


class Table(object):
    """
    Given a set of variables and respective domains, this data structure provides
    read/write access to a value assigned to each full combination of all variables.

    For N variables, each with K values, this means a total of K^N values.
    """
    def __init__(self, column_names):
        """
        Attributes
        ----------
        column_names : {str: [str]}
            Names of the columns that make up the table and a list of all possible values for each.
        """
        self._column_names = column_names

    def get_value(self, row):
        """
        Parameters
        ----------
        row : {str: str}
            Pairs of column name/value

        Preconditions
        -------------
        All columns' values should be specified.
        """
        raise NotImplementedError()

    def set_value(self, row, value):
        """ Set the value that corresponds with the provided combination of column/value.

        Preconditions
        -------------
        All columns' values should be specified.
        """
        raise NotImplementedError()


class FullTable(Table):
    def __init__(self, column_names):
        """
        Parameters
        ----------
        column_names : {str: [str]}
            See Table.

        Attributes
        ----------
        table : {name: {name: ... {name: value} ... }}
        variables : {name: [name]}
        order : [name]
        last : name
        """
        super(FullTable, self).__init__(column_names)

        # Sort the variables so the representation is more predictable
        self.order = list(self._column_names.keys())
        self.order.sort()

        self.last = self.order.pop()

        self.table = self.__make_table_rec(self.order)

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

            for value in self._column_names[self.last]:
                counts[value] = 0

            return counts
        else:
            current = {}

            for value in self._column_names[order[0]]:
                current[value] = self.__make_table_rec(order[1:])

            return current

    def set_value(self, row, value):
        current = self.table

        for name in self.order:
            if name not in row:
                raise IndexError("There is no variable {0} in this Table".format(name))
            current = current[row[name]]

        current[row[self.last]] = value

    def get_value(self, row):
        """
        Parameters
        ----------
        vals : {name: value}
        """
        current = self.table

        for name in self.order:
            current = current[row[name]]

        return current[row[self.last]]

    def increment_value(self, vals):
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

    def map_function_over_all_values(self, f):
        """
        Perform function f(x) on every element.

        Parameters
        ----------
        f : function x: f(x)
        """
        self.__map_function_over_all_values_recursive(f, self.table, self.order)

    def __map_function_over_all_values_recursive(self, f, current, order):
        if len(order) == 0:
            for value in current:
                current[value] = f(current[value])
        else:
            for value in current:
                self.__map_function_over_all_values_recursive(f, current[value], order[1:])


class SparseTable(Table):
    def __init__(self, column_names):
        super(SparseTable, self).__init__(column_names)

        self.table = {}
        self._column_names = column_names

        self.order = list(self._column_names.keys())
        self.order.sort()

        self.last = self.order.pop()

    def get_variables(self):
        return self._column_names.copy()

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

        current[entry[self.last]] = 0

    def set_value(self, row, value):
        current = self.table

        for name in self.order:
            if row[name] not in current:
                self.__make_entry(row)
                # try again, but now the entry exists
                self.set_value(row, value)
                return

            current = current[row[name]]

        if row[self.last] not in current:
            self.__make_entry(row)
            self.set_value(row, value)
            return
        else:
            current[row[self.last]] = value

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

        if vals[self.last] not in current:
            self.__make_entry(vals)
            self.set_value(vals, 1)
            return
        else:
            current[vals[self.last]] += 1

    def get_value(self, row):
        """
        Parameters
        ----------
        vals : {name: value}
        """
        current = self.table

        for name in self.order:
            if row[name] not in current:
                return 0

            current = current[row[name]]

        if row[self.last] not in current:
            return 0
        else:
            v = current[row[self.last]]
            return v

    def get_nonzero_entries(self):
        return self.__get_nonzero_entries_rec(self.table, self.order, {})

    def __get_nonzero_entries_rec(self, current, order, entry):
        if len(order) == 0:
            for value in current:
                new_entry = deepcopy(entry)
                new_entry[self.last] = value

                return [new_entry]
        else:
            entries = []
            for value in current:
                new_entry = deepcopy(entry)
                new_entry[order[0]] = value

                entries += self.__get_nonzero_entries_rec(current[value], order[1:], new_entry)

            return entries

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


class SparseConditionalTable(SparseTable):
    def __init__(self, column_names, conditional):
        super(SparseConditionalTable, self).__init__(column_names)

        self.conditional = conditional

        self.conditional_table = SparseTable(conditional)

    def set_value(self, row, value):
        super(SparseConditionalTable, self).set_value(row, value)

        # Add entry to the conditional table
        self.conditional_table.set_value({k: v for k, v in row.iteritems() if k in self.conditional.keys()}, True)

    def has_data(self, conditional):
        return self.conditional_table.get_value(conditional)


class Distribution(SparseTable):
    def __init__(self, column_names, freq=None):
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
            super(Distribution, self).__init__(column_names)
        elif isinstance(freq, SparseTable):
            self._column_names = deepcopy(freq._column_names)
            self.order = deepcopy(freq.order)
            self.last = deepcopy(freq.last)

            self.table = deepcopy(freq.table)
        else:
            raise RuntimeError("Not a Table.")

    def __eq__(self, other):
        if not isinstance(other, Distribution):
            return False

        # Check if variables and values are the same
        for variable in self._column_names:
            if variable not in other._column_names:
                return False
            else:
                a = self._column_names[variable]
                b = self._column_names[variable]

                if not set(a) == set(b):
                    return False

        # Check if all values are the same
        values = []
        for variable in self.order:
            values.append(self._column_names[variable])
        values.append(self._column_names[self.last])

        for combination in list(itertools.product(*values)):
            vals = {}
            for i in range(len(self.order)):
                vals[self.order[i]] = combination[i]
            vals[self.last] = combination[-1]

            if self.get_value(vals) != other.get_value(vals):
                return False

        return True

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
