__author__ = 'Dennis'

from copy import copy, deepcopy
import random
import itertools

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
        entries : {time: {name: value}}
            list of dictionaries of variable name/value pairs
        """
        self.entries = {}

    def add_entry(self, vals, time=-1):
        """
        Parameters
        ----------
        vals : {name: value}
            For every observed variable, what the value was for that observation.
        """
        if time == -1:
            self.entries[len(self.entries)] = deepcopy(vals)
        else:
            self.entries[time] = deepcopy(vals)

    def calculate_joint(self, actions, sensories):
        if len(self.entries) < 2:
            variables = {}
            variables.update(actions)
            variables.update(sensories)

            return self.calculate_joint_flat(variables)
        else:
            return self.calculate_joint_with_time(actions, sensories)

    def calculate_joint_flat(self, variables):
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

        for t in range(len(self.entries)):
            freq.inc_value(self.entries[t])

        n = len(self.entries)
        freq.do_operation(lambda x: x / float(n))

        return easl.utils.Distribution(variables, freq)

    def calculate_joint_with_time(self, actions, sensories):
        """
        Calculates the joint probability distribution from data for the given
        variables, but takes into account that actions come before consequences
        in time.
        """
        variables = actions
        variables.update(sensories)

        freq = easl.utils.Table(variables)

        # For the actions of every time step
        for t_i in range(len(self.entries) - 1):
            # and the sensories of the next
            for t_k in range(t_i, len(self.entries)):
                # Create the combined entry and update the frequency
                entry_i = self.entries[t_i]
                entry_k = self.entries[t_k]

                entry = {}

                for action in entry_i:
                    if action in actions:
                        entry[action] = entry_i[action]
                for sensory in entry_k:
                    if sensory in sensories:
                        entry[sensory] = entry_k[sensory]

                freq.inc_value(entry)

        n = len(self.entries)
        freq.do_operation(lambda x: x / float(n))

        return easl.utils.Distribution(variables, freq)


class CausalBayesNetLearner(object):
    """
    Implementation of the constraint-based approach to learning a causal Bayes
    net.
    """
    @staticmethod
    def step_2(actions, sensories, graph, data):
        """
        Parameters
        ----------
        variables : {name: [string]}
        """
        # 2. Test each pair of variables for independence.
        #    Eliminate the edges between any pair of variables found to be
        #    independent.
        #
        #    P(A) * P(B) = P(A & B)
        #    P(B|A) = P(B)
        #    P(A|B) = P(A)
        # Check independence by checking if P(A|B) = P(A)
        names = actions.keys() + sensories.keys()
        for i_a in range(len(names)):
            a = names[i_a]
            for b in names[i_a + 1:]:
                # Calculate P(A, B)
                p_ab = CausalBayesNetLearner.calculate_joint([a, b], actions, sensories, data)

                # Check for independence by checking P(A & B) = P(A) * P(B)
                if CausalLearningAgent.are_independent(a, b, p_ab):
                    graph.del_edge(a, b)

    @staticmethod
    def step_3(actions, sensories, graph, sepset, data):
        # 3. For each pair U, V of variables connected by an edge,
        #    and for each T connected to one or both U, V, test whether
        #    U _|_ V | T
        #    If an independence is found, remove the edge between U and V.
        #
        #    P(A,B|C) = P(A|C) * P(B|C)
        #    P(A,B,C)/P(C) = P(A,C)/P(C) * P(B,C)/P(C)
        # Get all pairs of nodes connected by an edge
        for (u, v) in graph.get_pairs():
            # Get all nodes connected to one of either nodes
            ts = set(graph.get_connected(u) + graph.get_connected(v))

            found = False

            for t in ts:
                # Test conditional independence
                # Calculate P(U,V,T)
                p_uvt = CausalBayesNetLearner.calculate_joint([u, v, t], actions, sensories, data)

                if CausalLearningAgent.are_conditionally_independent(u, v, [t], p_uvt):
                    found = True
                    continue

            if found:
                graph.del_edge(u, v)
                sepset.append((u, v))
                sepset.append((v, u))
                continue

    @staticmethod
    def step_4(actions, sensories, graph, sepset, data):
        # 4. For each pair U, V connected by an edge and each pair of T, S of
        #    variables, each of which is connected by an edge to either U or V,
        #    test the hypothesis that U _|_ V | {T, S}.
        #    If an independence is found, remove the edge between U, V.
        #
        #    P(A,B|C,D) = P(A|C,D) * P(B|C,D)
        #    P(A,B,C,D)/P(C,D) = P(A,C,D)/P(C,D) * P(B,C,D)/P(C,D)
        for (u, v) in graph.get_pairs():
            ts = graph.get_connected(u) + graph.get_connected(v)

            found = False
            for (t, s) in [(t, s) for t in ts for s in ts if t != s]:
                p_uvst = CausalBayesNetLearner.calculate_joint([u, v, s, t], actions, sensories, data)

                if CausalLearningAgent.are_conditionally_independent(u, v, [s, t], p_uvst):
                    found = True
                    continue

            if found:
                graph.del_edge(u, v)
                sepset.append((u, v))
                sepset.append((v, u))
                continue

    @staticmethod
    def step_5(graph, sepset):
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
        # get triples T - V - R
        for (t, v, r) in graph.get_triples():
            # if T - R not in sepset, orient edges
            if (t, r) not in sepset:
                graph.orient(t, v, r)

    @staticmethod
    def step_6(graph):
        # 6. For each triple of variables T, V, R such that T has an edge
        #    with an arrowhead directed into V and V - R, and T has no edge
        #    connecting it to R, orient V - R as V -> R.
        for (t, v, r) in graph.get_triples_special():
            graph.orient_half(v, r)

    @staticmethod
    def variables_from_names(names, variables):
        selection = {}
        for name in names:
            if name in variables:
                selection[name] = variables[name]

        return selection

    @staticmethod
    def calculate_joint(names, actions, sensories, data):
        return data.calculate_joint(CausalBayesNetLearner.variables_from_names(names, actions),
                                    CausalBayesNetLearner.variables_from_names(names, sensories))


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
    INITIAL_STATE = 0
    CALCULATE_NETWORK_STATE = 1
    ACTION_STATE = 2
    CHECK_CAUSALITY_STATE = 3

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
        time : int
            Internal time representation.
        """
        super(CausalLearningAgent, self).__init__()

        self.data = Data()

        self.actions = {}
        self.sensories = {}
        self.variables = {}

        self.signals = {}
        self.default_action = {}
        self.default_signals = {}
        self.observations = {}

        self.network = None

        self.values = {}
        self.time = 0

        self.state = CausalLearningAgent.INITIAL_STATE

    def init_internal(self, entity):
        """
        """
        self.time = 0
        # Get attributes with possible values
        attributes = copy(entity.attribute_values)

        # Get actions with possible values
        actions = {}
        # actions = {name: (function, [value])}
        # variables = {name: [value]}
        for action in entity.actions:
            actions[action] = entity.actions[action][1]

        # Get possible sensed signals
        signals = {}
        for sensor in entity.sensors:
            signals.update(sensor.signals)

            self.signals.update(sensor.signals)
            self.default_signals.update(sensor.default_signals)

        # Add all together into variables
        self.actions = actions
        self.default_action = entity.default_action

        self.sensories.update(attributes)
        self.sensories.update(signals)

        self.variables.update(self.sensories)
        self.variables.update(self.actions)

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
        name, value = observation

        self.observations[name] = value

    def act(self):
        # Convert observations into an entry in the Database.
        self.__store_observations()
        self.time += 1

        if self.state == CausalLearningAgent.INITIAL_STATE:
            print "initial"
            if self.time > 10:
                self.state = CausalLearningAgent.CALCULATE_NETWORK_STATE

            # Select actions at random
            return [self.__select_random_action()]
        elif self.state == CausalLearningAgent.CALCULATE_NETWORK_STATE:
            print "calculate"
            # Calculate the causal Bayes net
            self.network = self.__learn_causality()
            self.state = CausalLearningAgent.ACTION_STATE
            print self.network.edges
            return [self.__select_action()]
        elif self.state == CausalLearningAgent.ACTION_STATE:
            print "action"
            self.state = CausalLearningAgent.CHECK_CAUSALITY_STATE

            return [self.__select_action()]
        elif self.state == CausalLearningAgent.CHECK_CAUSALITY_STATE:
            print "check"
            # Do something to check if the expected observation is true now.
            self.state = CausalLearningAgent.ACTION_STATE

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

        self.data.add_entry(observations, self.time)
        self.observations = {}

    def __learn_causality(self):
        c = easl.utils.Graph()
        c.make_complete(self.variables.keys())

        sepset = []

        CausalBayesNetLearner.step_2(self.actions, self.sensories, c, self.data)
        CausalBayesNetLearner.step_3(self.actions, self.sensories, c, sepset, self.data)
        CausalBayesNetLearner.step_4(self.actions, self.sensories, c, sepset, self.data)
        CausalBayesNetLearner.step_5(c, sepset)
        CausalBayesNetLearner.step_6(c)

        return c

    def __select_action(self):
        """
        Selects one action by using the network and values that were set.

        Returns
        -------
        (name, value)
            The variable name and its value.
        """
        action = None
        # calculate argmax_A P(M=true | A)
        # for any variable M that we are 'interested in'
        for var_m in self.values:
            val_m = self.values[var_m]

            # Find actions A that have a path to M
            actions = self.network.causal_paths(var_m)

            # find argmax_A,a P(M=m | A=a) for actions A=a
            argmax = None
            for var_a in actions:
                for val_a in self.actions[var_a]:
                    p_ma = CausalBayesNetLearner.calculate_joint([var_m, var_a], self.variables, self.data)

                    p_conditional = CausalLearningAgent.conditional_probability([var_m, var_a], p_ma, val_m, val_a)
                    self.log.do_log("probability", {"probability": p_conditional, "action": var_a, "value": val_a})
                    if argmax is None:
                        argmax = (var_a, val_a, p_conditional)
                    elif p_conditional > argmax[2]:
                        argmax = (var_a, val_a, p_conditional)

            if argmax is not None and argmax[2] != 0:
                action = (argmax[0], argmax[1])

        # if none selected, select at random (?)
        if action is None:
            action = self.__select_random_action()

        return action

    def __select_random_action(self):
        print "RANDOM"
        a = random.choice(self.actions.keys())
        v = random.choice(self.actions[a])

        return a, v

    @staticmethod
    def conditional_probability(names, ab, val_a, val_b):
        """
        P(A=a | B=b) = P(A=a & B=b) / P(B=b)

        Parameters
        ----------
        names : (string, string)
            Names of variables A, B respectively.
        ab : Distribution
        b : Distribution
        val_a : value
            a in A=a
        val_b : value
            b in B=b
        """
        var_a, var_b = names

        p_ab = ab.partial_prob({var_a: val_a, var_b: val_b})
        p_b = ab.partial_prob({var_b: val_b})

        return 0 if p_b == 0 else p_ab / p_b

    @staticmethod
    def are_independent(a, b, d):
        """
        Checks the distributions according to P(A & B) = P(A) * P(B)

        Parameters
        ----------
        a : string
            Name of variable A
        b : string
            Name of variable B
        d : Distribution
            Distribution containing variables A and B.
        """
        # Check for all possible values of the parameters of A and B
        for val_a in d.get_variable_values(a):
            for val_b in d.get_variable_values(b):
                # P(A & B) = P(A) * P(B)
                p_ab = d.partial_prob({a: val_a, b: val_b})
                p_a = d.single_prob(a, val_a)
                p_b = d.single_prob(b, val_b)

                # When the probabilities are not 'equal'
                if abs(p_ab - p_a * p_b) > 1e-6:
                    return False
        return True

    @staticmethod
    def are_conditionally_independent(a, b, y, d):
        """
        Calculates the conditional probability.

        P(A,B|C) = P(A|C) * P(B|C)
        P(A,B,C)/P(C) = P(A,C)/P(C) * P(B,C)/P(C)

        Generalized:
        P(A,B|Y) = P(A|Y) * P(B|Y)
        P(A,B,Y) / P(Y) = P(A,Y) / P(Y) * P(B,Y) / P(Y)

        Parameters
        ----------
        a : string
            Name for variable A.
        b : string
            Name for variable B.
        y : [string]
            Names for the conditional variables Y.
        d : Distribution
        """
        values = [d.get_variable_values(variable) for variable in y]

        for val_a in d.get_variable_values(a):
            for val_b in d.get_variable_values(b):
                vals_aby = {a: val_a, b: val_b}
                vals_ay = {a: val_a}
                vals_by = {b: val_b}
                vals_y = {}

                for combination in list(itertools.product(*values)):
                    for i in range(len(combination)):
                        x = y[i]

                        vals_aby[x] = combination[i]
                        vals_ay[x] = combination[i]
                        vals_by[x] = combination[i]
                        vals_y[x] = combination[i]

                    p_aby = d.partial_prob(vals_aby)
                    p_ay = d.partial_prob(vals_ay)
                    p_by = d.partial_prob(vals_by)
                    p_y = d.partial_prob(vals_y)

                    # P(A,B,Y) / P(Y) = P(A,Y) / P(Y) * P(B,Y) / P(Y)
                    if p_y != float(0):
                        left = p_aby / float(p_y)
                        right = (p_ay / float(p_y)) * (p_by / float(p_y))

                        if abs(left - right) > 1e-6:
                            return False
        return True
