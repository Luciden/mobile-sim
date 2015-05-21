__author__ = 'Dennis'

from copy import deepcopy
import random
import itertools

import easl.utils
from controller import Controller


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

    def calculate_joint(self, variables):
        if len(self.entries) < 2:
            return self.calculate_joint_flat(variables)
        else:
            return self.calculate_joint_with_time(variables)

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

    def calculate_joint_with_time(self, variables):
        """
        Calculates the probability of taking actions from previous time step and
        sensories from next.
        """
        freq = easl.utils.Table(variables)

        entries = []

        for t_i in self.entries:
            t_k = t_i + 1
            if t_k not in self.entries:
                continue

            entry = {}
            for variable in variables:
                if variable.endswith("_prev"):
                    # Strip the _prev part because it's not stored in the data
                    name = variable[:-5]
                    entry[variable] = self.entries[t_i][name]
                else:
                    entry[variable] = self.entries[t_k][variable]

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
    def step_2(variables, graph, data):
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
        names = variables.keys()

        for i_a in range(len(names)):
            a = names[i_a]
            for b in names[i_a + 1:]:
                # Calculate P(A, B)
                p_ab = CausalBayesNetLearner.calculate_joint([a, b], variables, data)

                # Check for independence by checking P(A & B) = P(A) * P(B)
                if CausalLearningController.are_independent(a, b, p_ab):
                    graph.del_edge(a, b)

    @staticmethod
    def step_3(variables, graph, sepset, data):
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
                p_uvt = CausalBayesNetLearner.calculate_joint([u, v, t], variables, data)

                if CausalLearningController.are_conditionally_independent(u, v, [t], p_uvt):
                    graph.del_edge(u, v)
                    sepset[u][v].append(t)
                    sepset[v][u].append(t)
                    continue

    @staticmethod
    def step_4(variables, graph, sepset, data):
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

                p_uvst = CausalBayesNetLearner.calculate_joint([u, v, s, t], variables, data)

                if CausalLearningController.are_conditionally_independent(u, v, [s, t], p_uvst):
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
            elif name.endswith("_prev"):
                if name[:-5] in variables:
                    selection[name] = variables[name[:-5]]

        return selection

    @staticmethod
    def calculate_joint(names, variables, data):
        return data.calculate_joint(CausalBayesNetLearner.variables_from_names(names, variables))


class CausalLearningController(Controller):
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
        super(CausalLearningController, self).__init__()

        self.data = Data()

        self.observations = {}

        self.action = (None, None)
        self.aim = (None, None)

        self.network = None
        self.variables_time = {}

        self.values = {}
        self.time = 0

        self.state = CausalLearningController.INITIAL_STATE
        self.exploration = []

    def init_internal(self, entity):
        """
        """
        super(CausalLearningController, self).init_internal(entity)

        self.time = 0

        self.exploration = self.__create_exploration_shuffle(repeat=4)

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
                self.log.do_log("observation", {"controller": "causal", "name": action[0], "value": action[1]})
                self.sense(action)

        return actions

    def __create_exploration_random(self, n=30):
        exploration = []

        for i in range(0, n):
            a = random.choice(self.actions)
            v = random.choice(self.actions[a])

            exploration.append((a, v))

        return exploration

    def __create_exploration_shuffle(self, repeat=1):
        """
        Perform a Knuth Shuffle on all possible actions.

        Notes
        -----
        http://en.wikipedia.org/wiki/Fisher%E2%80%93Yates_shuffle
        """
        # Generate all possible actions
        actions = self.all_actions(self.actions)

        # for i from n - 1 down to 1
        for i in range(len(actions) - 1, 0, -1):
            # j = random integer such that 0 <= j <= i
            j = random.randint(0, i)
            # exchange a[i] and a[j]
            actions[i], actions[j] = actions[j], actions[i]

        exploration = []

        for i in range(0, repeat):
            exploration.extend(actions)

        return exploration

    @staticmethod
    def all_actions(actions):
        """
        Parameters
        ----------
        actions : {name: [value]}

        Returns
        -------
        [(name, value)]
            List of all action/value pairs from a set of action descriptions.
        """
        combinations = []
        for action in actions:
            for value in actions[action]:
                combinations.append((action, value))

        return combinations

    def __act(self):
        # Convert observations into an entry in the Database.
        self.time += 1
        self.__store_observations()

        if self.state == CausalLearningController.INITIAL_STATE:
            print "initial"

            action = self.exploration.pop(0)

            if len(self.exploration) == 0:
                self.state = CausalLearningController.CALCULATE_NETWORK_STATE

            return [action]
            """

            # Select an action at random
            action = self.__select_random_action()

            # Perform the action, then calculate the network in the next step
            self.state = CausalLearningAgent.CALCULATE_NETWORK_STATE

            return [action]
            """

        if self.state == CausalLearningController.CALCULATE_NETWORK_STATE:
            print "calculate"
            # Calculate the causal Bayes net
            self.network = self.__learn_causality()
            self.network.visualize()
            # then start checking the network
            self.state = CausalLearningController.ACTION_STATE

        if self.state == CausalLearningController.CHECK_CAUSALITY_STATE:
            # Do something to check if the expected observation is true now.
            # then skip to ACTION_STATE
            print "check"
            self.state = CausalLearningController.ACTION_STATE

            # Check if the aim is in the observations
            entry = self.data.get_entries_at_time(self.time)

            if entry[self.aim[0]] != self.aim[1]:
                # Remove the edge
                self.network.del_edge(self.action[0], self.aim[0])

        if self.state == CausalLearningController.ACTION_STATE:
            print "action"
            self.state = CausalLearningController.CHECK_CAUSALITY_STATE

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
        # Create complete graph of previous actions and sensories, and current sensories
        c = easl.utils.Graph()
        self.variables_time = {}
        self.variables_time.update(self.sensory)
        for variable in self.actions:
            self.variables_time[variable + "_prev"] = self.actions[variable]
        for variable in self.sensory:
            self.variables_time[variable + "_prev"] = self.sensory[variable]

        c.make_complete(self.variables_time.keys())

        sepset = {}
        for a in self.variables_time:
            sepset[a] = {}
            for b in self.variables_time:
                if a == b:
                    continue
                sepset[a][b] = []

        CausalBayesNetLearner.step_2(self.variables_time, c, self.data)
        CausalBayesNetLearner.step_3(self.variables_time, c, sepset, self.data)
        CausalBayesNetLearner.step_4(self.variables_time, c, sepset, self.data)
        CausalBayesNetLearner.step_5(c, sepset)
        CausalBayesNetLearner.step_6(c)

        return c

    def __make_variables_from_names(self, names):
        selection = {}

        for name in names:
            if name in self.variables:
                selection[name] = self.variables[name]
            elif name.endswith("_prev"):
                if name[:-5] in self.variables:
                    selection[name] = self.variables[name[:-5]]
            else:
                raise Exception("Name {0} not in variables.".format(name))

        return selection

    def __select_maximizing_action(self, variable, value):
        """
        Selects one action by using the network and values that were set.

        Parameters
        ----------
        variable : string
        value : value

        Returns
        -------
        (name, value)
            The variable name and its value.
        """
        # find argmax_A,a P(M=m | A=a) for actions A=a
        selected = None
        argmax = None
        # Get all causal paths to the variable under consideration
        for path in self.network.causal_paths(variable):
            name = path[0]
            # Check only variables that are actions,
            #
            if not name.endswith("_prev") or name[:-5] not in self.actions:
                continue
            # Remove the "_prev" part
            action = name[:-5]

            for val_a in self.actions[action]:
                p_ma = CausalBayesNetLearner.calculate_joint([variable, action],
                                                             self.variables_time,
                                                             self.data)

                p_conditional = CausalLearningController.conditional_probability([variable, action], p_ma, value, val_a)
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
