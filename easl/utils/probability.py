__author__ = 'Dennis'

class Distribution(object):
    def __init__(self, variables):
        self.table = {}
        self.variables = variables

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
        return self._single_prob_rec(variable, value, self.table, self.order)

    def _single_prob_rec(self, variable, value, current, order):
        p = 0

        # if variable is found, sum all probabilities in branch with appropriate value
        if order[0] == variable:
            p += self._sum_prob_rec(current[value], order[1:])
        # keep searching for variable and take all branches into account
        else:
            for branch in current:
                p += self._single_prob_rec(variable, value, current[branch], order[1:])

        return p

    def _sum_prob_rec(self, current, order):
        p = 0
        if len(order) == 0:
            for value in current:
                p += current[value]
        else:
            for value in current:
                p += self._sum_prob_rec(current[value], order[1:])

        return p
