__author__ = 'Dennis'

from copy import copy, deepcopy
import random

import easl.utils
from agent import Agent


class Data(object):
    """
    Stores all previous observations.
    """
    def __init__(self):
        """
        Attributes
        ----------
        entries : [{name: value}]
            list of dictionaries of variable name/value pairs
        """
        self.entries = []

    def add_entry(self, vals):
        """
        Parameters
        ----------
        vals : {name: value}
            For every observed variable, what the value was for that observation.
        """
        # TODO: For some reason Data always gets the same entry.
        self.entries.append(deepcopy(vals))

    def calculate_joint(self, variables):
        """
        Calculates the joint probability distribution from data for the given
        variables.

        Parameters
        ----------
        variables : {name: {name: [value]}}
            The variable names with their parameters and possible values for which
            to calculate the distribution.

        Returns
        -------
        Distribution
            the joint probability table
        """
        freq = easl.utils.Table(variables)

        for entry in self.entries:
            freq.inc_value(entry)

        n = len(self.entries)
        freq.do_operation(lambda x: x / n)

        return easl.utils.Distribution(variables, freq)


class CausalLearningAgent(Agent):
    """
    Uses Causal Bayes Nets based learning.

    Needs
     - conversion of observations to Variables
     - actions as interventions

    Attributes
    ----------
    variables : {name: {name: value}}
        All variable names that are considered at the moment.

    Notes
    -----
    Based on work by Gopnik [1]_ and dissertation [2]_.

    Probability:
    http://www.saedsayad.com/naive_bayesian.htm

    References
    ----------
    .. [1] "Thing by Gopnik," Gopnik et al.
    .. [2] Dissertation
    """

    def __init__(self):
        """
        Attributes
        ----------
        data : Data
            Stores previous observations.
            Used to calculate (conditional) probabilities.
        actions : {name: [value]}
        default_action : {name: value}
        default_signals : {name: value}
        network : Graph
        observations : {name: value}
        variables : {name: [value]}
        values : {name: value}
            Variable/value pairs that have value set to '1' for action selection.
        """
        # TODO: Make sure variables has all variable names/values that will be be observed.
        # TODO: Make sure that all variables always have values assigned when sensed.
        super(CausalLearningAgent, self).__init__()

        self.data = Data()

        self.actions = {}
        self.signals = {}
        self.default_action = {}
        self.default_signals = {}
        self.observations = {}

        self.variables = {}
        self.network = None

        self.values = {}

    def init_internal(self, entity):
        """
        """
        # Get attributes with possible values
        attributes = copy(entity.attribute_values)

        # Get actions with possible values
        actions = {}
        # actions = {name: (function, [value])}
        # variables = {name: [value]}
        for action in entity.actions:
            actions[action] = entity.actions[action][1]

        self.actions = actions
        self.default_action = entity.default_action

        # Get possible sensed signals
        signals = {}
        for sensor in entity.sensors:
            signals.update(sensor.signals)

            self.signals.update(sensor.signals)
            self.default_signals.update(sensor.default_signals)

        # Add all together into variables
        self.variables.update(attributes)
        self.variables.update(actions)
        self.variables.update(signals)

    def set_values(self, vals):
        """
        Sets the values that are used for action selection.

        All variable/value pairs that are provided will have its value set to 1.
        All others are considered to be 0.

        Parameters
        ----------
        vals : {name: value}
            The variable/value pairs for which to set the value to 1.
        """
        self.values.update(vals)

    def sense(self, observation):
        """
        Parameters
        ----------
        observation : (name, value)
        """
        # Simply store the information to use later.
        self.observations.update(observation)

    def act(self):
        # Convert observations into an entry in the Database.
        self.__store_observations()

        # Get the causal network for the observations.
        self.network = self.__learn_causality(self.variables.keys())
        # Find the action that would create the optimal reward.
        return [self.__select_action()]

    def __store_observations(self):
        """
        Takes the observations in this time step and stores them in the database.

        Makes sure all variables under consideration are present.
        """
        observations = {}
        for variable in self.variables:
            # Take the variables that were observed as-is
            if variable in self.observations:
                observations[variable] = self.observations[variable]
            # If the variable was not observed, but is an action, take the default
            elif variable in self.actions:
                observations[variable] = self.default_action[variable]
            # If the variable was not observed, but is a signal, take the default
            elif variable in self.signals:
                observations[variable] = self.default_signals[variable]
            else:
                raise RuntimeError("Variable {0} not in observation".format(variable))

        self.data.add_entry(observations)
        self.observations = {}

    def __learn_causality(self, variables):
        """
        Constraint-based approach to learning the network.

        Parameters
        ----------
        variables : list
            network node names
        data : list of list
            contains data on variable instances used to check for independence
            a table of entries of lists of variable/value pairs
        """
        # 1. Form the complete undirected graph on all variables
        c = easl.utils.Graph()
        c.make_complete(variables)

        sepset = []

        # 2. Test each pair of variables for independence.
        #    Eliminate the edges between any pair of variables found to be
        #    independent.
        #
        #    P(A) * P(B) = P(A & B)
        #    P(B|A) = P(B)
        #    P(A|B) = P(A)
        self.__learn_causality_step_2(variables, c)

        # 3. For each pair U, V of variables connected by an edge,
        #    and for each T connected to one or both U, V, test whether
        #    U _|_ V | T
        #    If an independence is found, remove the edge between U and V.
        #
        #    P(A,B|C) = P(A|C) * P(B|C)
        #    P(A,B,C)/P(C) = P(A,C)/P(C) * P(B,C)/P(C)
        # Get all pairs of nodes connected by an edge
        self.__learn_causality_step_3(c, sepset)

        # 4. For each pair U, V connected by an edge and each pair of T, S of
        #    variables, each of which is connected by an edge to either U or V,
        #    test the hypothesis that U _|_ V | {T, S}.
        #    If an independence is found, remove the edge between U, V.
        #
        #    P(A,B|C,D) = P(A|C,D) * P(B|C,D)
        #    P(A,B,C,D)/P(C,D) = P(A,C,D)/P(C,D) * P(B,C,D)/P(C,D)
        self.__learn_causality_step_4(c, sepset)

        # 5. For each triple of variables T, V, R such that T - V - R and
        #    there is no edge between T and R, orient as To -> V <- oR if
        #    and only if V was not conditioned on when removing the T - R
        #    edge.
        #
        #    The last part means to keep record of which edges were removed
        #    and to check against those.
        #
        #    According to Spirtes et al. this means leaving the original
        #    mark on the T and R nodes and putting arrow marks on the V
        #    end.
        self.__learn_causality_step_5(c, sepset)

        # 6. For each triple of variables T, V, R such that T has an edge
        #    with an arrowhead directed into V and V - R, and T has no edge
        #    connecting it to R, orient V - R as V -> R.
        self.__learn_causality_step_6(c)

        return c

    def __learn_causality_step_2(self, variables, graph):
        # Check independence by checking if P(A|B) = P(A)
        for i_a in range(len(variables)):
            a = variables[i_a]
            for b in variables[i_a + 1:]:
                # Calculate P(A)
                p_a = self.__calculate_joint([a])

                # Calculate P(B)
                p_b = self.__calculate_joint([b])

                # Calculate P(A & B)
                p_ab = self.__calculate_joint([a, b])

                # Check for independence by checking P(A & B) = P(A) * P(B)
                if CausalLearningAgent.check_independence((a, b), p_a, p_b, p_ab):
                    graph.del_edge(a, b)

    def __learn_causality_step_3(self, graph, sepset):
        for (u, v) in graph.get_pairs():
            # Get all nodes connected to one of either nodes
            ts = set(graph.get_connected(u) + graph.get_connected(v))

            found = False

            for t in ts:
                # Test conditional independence
                # Calculate P(T), P(U,T), P(V,T) and P(U,V,T)
                p_t = self.__calculate_joint([t])
                p_ut = self.__calculate_joint([u, t])
                p_vt = self.__calculate_joint([v, t])
                p_uvt = self.__calculate_joint([u, v, t])

                if CausalLearningAgent.check_independence_conditional([u, v, t],
                                                                      p_uvt, p_ut, p_vt, p_t):
                    found = True
                    continue

            if found:
                graph.del_edge(u, v)
                sepset.append((u, v))
                sepset.append((v, u))
                continue

    def __learn_causality_step_4(self, graph, sepset):
        for (u, v) in graph.get_pairs():
            ts = graph.get_connected(u) + graph.get_connected(v)

            found = False
            for (t, s) in [(t, s) for t in ts for s in ts if t != s]:
                p_uvst = self.__calculate_joint([u, v, s, t])
                p_ust = self.__calculate_joint([u, s, t])
                p_vst = self.__calculate_joint([v, s, t])
                p_st = self.__calculate_joint([s, t])

                if CausalLearningAgent.check_independence_conditional([u, v, s, t],
                                                                      p_uvst, p_ust, p_vst, p_st):
                    found = True
                    continue

            if found:
                graph.del_edge(u, v)
                sepset.append((u, v))
                sepset.append((v, u))
                continue

    def __learn_causality_step_5(self, graph, sepset):
        # get triples T - V - R
        for (t, v, r) in graph.get_triples():
            # if T - R not in sepset, orient edges
            if (t, r) not in sepset:
                graph.orient(t, v, r)

    def __learn_causality_step_6(self, graph):
        for (t, v, r) in graph.get_triples_special():
            graph.orient_half(v, r)

    def __select_action(self):
        """
        Selects one action by using the network and values that were set.

        Returns
        -------
        (name, value)
            The variable name and its value.
        """
        # TODO: Fix. Probabilities do not seem to update.
        action = None
        # calculate argmax_A P(M=true | A)
        # for any variable M that we are 'interested in'
        for var_m in self.values:
            val_m = self.values[var_m]

            # find argmax_A,a P(M=m | A=a) for actions A=a
            argmax = None
            for var_a in self.actions:
                for val_a in self.actions[var_a]:
                    p_ma = self.__calculate_joint([var_m, var_a])
                    p_a = self.__calculate_joint([var_a])

                    p_conditional = CausalLearningAgent.conditional_probability([var_m, var_a], p_ma, p_a, val_m, val_a)
                    if argmax is None:
                        argmax = (var_a, val_a, p_conditional)
                    elif p_conditional > argmax[2]:
                        argmax = (var_a, val_a, p_conditional)

            if argmax is not None and argmax[2] != 0:
                action = (argmax[0], argmax[1])

        # if none selected, select at random (?)
        if action is None:
            print "RANDOM"
            a = random.choice(self.actions.keys())
            v = random.choice(self.actions[a])
            action = (a, v)

        return action

    @staticmethod
    def conditional_probability(names, ab, b, val_a, val_b):
        """
        P(A=a | B=b) = P(A=a & B=b) / P(B=b)
        """
        var_a, var_b = names

        p_ab = ab.prob({var_a: val_a, var_b: val_b})
        p_b = b.prob({var_b: val_b})

        return 0 if p_b == 0 else p_ab / p_b

    @staticmethod
    def check_independence(names, a, b, ab):
        """
        Checks the distributions according to P(A & B) = P(A) * P(B)

        Parameters
        ----------
        names : (string, string)
            Names for variable A and B respectively.
        a : Distribution
        b : Distribution
        ab : Distribution
            Joint probability distributions calculated from the data.
            These list for every variable and their possible values what
            the probability is.
        Returns
        -------
        bool
            True if A and B pass the independence check, False otherwise
        """
        # Assume the distributions are correct
        # Get variables
        var_a, var_b = names
        v_a = a.get_variables()
        v_b = b.get_variables()

        # Check for all possible values of the parameters of A and B
        for val_a in v_a[var_a]:
            for val_b in v_b[var_b]:
                # P(A & B) = P(A) * P(B)
                p_ab = ab.prob({var_a: val_a, var_b: val_b})
                p_a = a.prob({var_a: val_a})
                p_b = b.prob({var_b: val_b})

                # When the probabilities are not 'equal'
                if abs(p_ab - p_a * p_b) > 1e-6:
                    return False
        return True

    @staticmethod
    def check_independence_conditional(names, aby, ay, by, y):
        """
        Calculates the conditional probability.

        P(A,B|C) = P(A|C) * P(B|C)
        P(A,B,C)/P(C) = P(A,C)/P(C) * P(B,C)/P(C)

        Generalized:
        P(A,B|Y) = P(A|Y) * P(B|Y)
        P(A,B,Y) / P(Y) = P(A,Y) / P(Y) * P(B,Y) / P(Y)

        Parameters
        ----------
        names : [string]
        aby :
        ay :
        by :
        y :
        """
        # TODO: Make this more readable/maintainable/beautiful.
        v_aby = aby.get_variables()
        var_a = names[0]
        var_b = names[1]
        vars_y = names[2:]

        # Systematically loop through all possible assignments of values to
        # the considered variables,
        # and check if the conditional probability equality holds.
        s_aby = {}
        s_ay = {}
        s_by = {}
        s_y = {}
        for val_a in v_aby[var_a]:
            s_aby[var_a] = val_a
            s_ay[var_a] = val_a
            for val_b in v_aby[var_b]:
                s_aby[var_b] = val_b
                s_by[var_b] = val_b
                for var_x in vars_y:
                    for val_x in vars_y[var_x]:
                        s_aby[var_x] = val_x
                        s_ay[var_x] = val_x
                        s_by[var_x] = val_x
                        s_y[var_x] = val_x

                        # P(A,B,C)/P(C) = P(A,C)/P(C) * P(B,C)/P(C)
                        p_aby = aby.prob(s_aby)
                        p_ay = ay.prob(s_ay)
                        p_by = by.prob(s_by)
                        p_y = y.prob(s_y)

                        # When the probabilities are not 'equal'
                        if abs(p_aby / p_y - (p_ay / p_y) * (p_by / p_y)) > 1e-6:
                            return False
        return True

    def __variables_from_names(self, names):
        variables = {}
        for name in names:
            variables[name] = self.variables[name]

        return variables

    def __calculate_joint(self, names):
        return self.data.calculate_joint(self.__variables_from_names(names))
