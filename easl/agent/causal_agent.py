__author__ = 'Dennis'

from copy import deepcopy
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

    def get_entries_at_time(self, time):
        return self.entries[time]

    def calculate_joint(self, actions, sensories):
        if len(actions) == 0 or len(self.entries) < 2:
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

        for entry in self.entries:
            freq.inc_value(self.entries[entry])

        n = len(self.entries)
        freq.do_operation(lambda x: x / float(n))

        return easl.utils.Distribution(variables, freq)

    def calculate_joint_with_time(self, actions, sensories):
        """
        Calculates the probability of taking actions from previous time step and
        sensories from next.
        """
        variables = {}
        variables.update(actions)
        variables.update(sensories)

        freq = easl.utils.Table(variables)

        entries = []

        for t_i in self.entries:
            t_k = t_i + 1
            if t_k not in self.entries:
                continue

            entry = {}
            for action in actions:
                if action in self.entries[t_i]:
                    entry[action] = self.entries[t_i][action]
            for sensory in sensories:
                if sensory in self.entries[t_k]:
                    entry[sensory] = self.entries[t_k][sensory]

            entries.append(entry)

        for entry in entries:
            freq.inc_value(entry)

        n = len(entries)
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

            for t in ts:
                if t == u or t == v:
                    continue
                # Test conditional independence
                # Calculate P(U,V,T)
                p_uvt = CausalBayesNetLearner.calculate_joint([u, v, t], actions, sensories, data)

                if CausalLearningAgent.are_conditionally_independent(u, v, [t], p_uvt):
                    graph.del_edge(u, v)
                    sepset[u][v].append(t)
                    sepset[v][u].append(t)
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

            for (t, s) in [(t, s) for t in ts for s in ts if t != s]:
                if t == u or t == v or s == u or s == v:
                    continue

                p_uvst = CausalBayesNetLearner.calculate_joint([u, v, s, t], actions, sensories, data)

                if CausalLearningAgent.are_conditionally_independent(u, v, [s, t], p_uvst):
                    graph.del_edge(u, v)
                    sepset[u][v].extend([s, t])
                    sepset[v][u].extend([s, t])

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
            if graph.is_edge(t, r):
                continue

            if v not in sepset[t][r]:
                graph.orient_half(t, v, "o")
                graph.orient_half(r, v, "o")

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
        signals : {name: [value]}
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

        self.observations = {}

        self.action = (None, None)
        self.aim = (None, None)

        self.network = None

        self.values = {}
        self.time = 0

        self.state = CausalLearningAgent.INITIAL_STATE

    def init_internal(self, entity):
        """
        """
        super(CausalLearningAgent, self).init_internal(entity)

        self.time = 0

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
        actions = self.__act()
        for action in actions:
                self.log.do_log("observation", {"agent": "causal", "name": action[0], "value": action[1]})
                self.sense(action)

        return actions

    def __act(self):
        # Convert observations into an entry in the Database.
        self.time += 1
        self.__store_observations()

        if self.state == CausalLearningAgent.INITIAL_STATE:
            print "initial"
            if self.time > 30:
                self.state = CausalLearningAgent.CALCULATE_NETWORK_STATE

            # Select actions at random
            return [self.__select_random_action()]

        if self.state == CausalLearningAgent.CALCULATE_NETWORK_STATE:
            # Calculate the causal Bayes net
            # then skip to ACTION_STATE
            print "calculate"
            self.network = self.__learn_causality()
            self.state = CausalLearningAgent.ACTION_STATE
            print self.network.edges

        if self.state == CausalLearningAgent.CHECK_CAUSALITY_STATE:
            # Do something to check if the expected observation is true now.
            # then skip to ACTION_STATE
            print "check"
            self.state = CausalLearningAgent.ACTION_STATE

            # Check if the aim is in the observations
            entry = self.data.get_entries_at_time(self.time)

            if entry[self.aim[0]] != self.aim[1]:
                # Remove the edge
                self.network.del_edge(self.action[0], self.aim[0])

        if self.state == CausalLearningAgent.ACTION_STATE:
            print "action"
            self.state = CausalLearningAgent.CHECK_CAUSALITY_STATE

            # Select action with highest probability of resulting in wanted
            # state.
            # Make sure to check if the state is true in the next step.
            # Otherwise remove edge.
            # Choose one value to aim for
            self.aim = a, v = self.__select_aim()

            action = self.__select_maximizing_action(a, v)
            if action is None:
                action = self.__select_random_action()
            self.action = action

            return [action]

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
                observations[variable] = self.default_signal[variable]
            else:
                raise RuntimeError("Variable {0} not in observation".format(variable))

        self.data.add_entry(observations, self.time)
        self.observations = {}

    def __select_aim(self):
        a = random.choice(self.values.keys())

        return a, self.values[a]

    def __learn_causality(self):
        c = easl.utils.Graph()
        c.make_complete(self.variables.keys())

        sepset = {}
        for a in self.variables:
            sepset[a] = {}
            for b in self.variables:
                if a == b:
                    continue

                sepset[a][b] = []

        CausalBayesNetLearner.step_2(self.actions, self.sensory, c, self.data)
        CausalBayesNetLearner.step_3(self.actions, self.sensory, c, sepset, self.data)
        CausalBayesNetLearner.step_4(self.actions, self.sensory, c, sepset, self.data)
        CausalBayesNetLearner.step_5(c, sepset)
        CausalBayesNetLearner.step_6(c)

        return c

    def __select_action(self):
        actions = []
        for variable in self.values:
            actions.append(self.__select_maximizing_action(variable, self.values[variable]))

        return actions

    def __select_maximizing_action(self, variable, value):
        """
        Selects one action by using the network and values that were set.

        Returns
        -------
        (name, value)
            The variable name and its value.
        """
        selected = None
        # calculate argmax_A P(M=true | A)
        # for any variable M that we are 'interested in'
        # Find actions A that have a path to M
        actions = self.network.causal_paths(variable)

        # find argmax_A,a P(M=m | A=a) for actions A=a
        argmax = None
        for path in actions:
            action = path[0]
            # Check only variables that are actions
            if action not in self.actions:
                continue

            for val_a in self.actions[action]:
                p_ma = CausalBayesNetLearner.calculate_joint([variable, action],
                                                             self.actions, self.variables, self.data)

                p_conditional = CausalLearningAgent.conditional_probability([variable, action], p_ma, value, val_a)
                if argmax is None:
                    argmax = (action, val_a, p_conditional)
                elif p_conditional > argmax[2]:
                    argmax = (action, val_a, p_conditional)

        if argmax is not None and argmax[2] != 0:
            selected = (argmax[0], argmax[1])
            self.log.do_log("max_probability", {"probability": argmax[2], "action": argmax[0], "value": argmax[1]})

        return selected

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
