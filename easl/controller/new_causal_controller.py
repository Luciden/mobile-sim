__author__ = 'Dennis'

import easl
from easl.utils import SparseTable
from controller import Controller
from easl import visualize

import random
import itertools
from copy import deepcopy


class Data(object):
    def __init__(self):
        self.entries = []

    def add_entry(self, vals):
        self.entries.append(deepcopy(vals))

    def get_entries_at_time(self, time):
        return self.entries[time]

    def get_entries_previous_current(self, time):
        if time >= len(self.entries) or time - 1 < 0:
            return {}

        previous = self.entries[time - 1]
        current = self.entries[time]

        previous = {x + NewCausalController.PREVIOUS: y for (x, y) in previous.iteritems()}
        current = {x + NewCausalController.CURRENT: y for (x, y) in current.iteritems()}

        entries = {}
        entries.update(previous)
        entries.update(current)

        return entries

    def last_time(self):
        return len(self.entries) - 1


class CausalLearningVisual(visualize.Visual):
    @staticmethod
    def visualize(self):
        group = visualize.Group("causal")
        if self.network is not None:
            group.add_element(visualize.Graph("graph", self.network, self.network.get_nodes(), self.network.get_edges()))

        return group


class NewCausalController(Controller):
    """
    """
    # Exploration phase: random movement to collect data
    STATE_EXPLORATION = 0
    # Experiment phase: phase after the exploration phase; learn association with environment
    STATE_EXPERIMENT = 1

    # suffixes to use for the current/previous nodes in the network
    PREVIOUS = "_previous"
    CURRENT = "_current"

    def __init__(self):
        """
        Attributes
        ----------
        state
            Current algorithm state/phase.
        exploration_iterations : int
            Number of iterations of the exploration phase.
        ignored_variables : [string]
            Variables that are ignored in the exploration phase.
        nodes : {int: string}
            Numbers/names of the network's nodes in the exploration phase.
        node_values : {string: [string]}
            Possible values for each node.
        numberings: {string: int}
            Inverted `nodes`.
        nodes_exp
            Similar to `nodes`, but for the variables that were ignored in the exploration phase.
        node_values_exp
            See `nodes_exp`
        numberings_exp
            See `nodes_exp`
        current_number : int
            Used to create a numbering of nodes that is used to determine the network's edges' directions.
        data : Data
            Stores previous information from environment and motor signals.
        network : Graph
            Causal network that is calculated every iteration; is stored for reference.
        jpd2 : Distribution
        current_information : {string: string}
            Variable assignments at the current iteration from the environment.
        new_information : {string: string}
            Similar to `current_information` but includes motor signals.
        iteration : int
            Internal count for which iteration the algorithm is running; used for data storage.

        selection_bias : float
            Determines by which probability a 'still' motor signal is chosen.
            TODO: Hacked specifically for the babybot now; might be necessary to generalize later.
        """
        super(NewCausalController, self).__init__(visual=CausalLearningVisual())

        self.state = self.STATE_EXPLORATION
        self.exploration_iterations = 5

        self.ignored_variables = []

        self.nodes = {}
        self.node_values = {}
        self.numberings = {}

        self.nodes_exp = {}
        self.node_values_exp = {}
        self.numberings_exp = {}

        self.current_number = 1

        self.data = Data()
        self.data2 = Data()
        self.network = None
        self.jpd2 = None

        self.current_information = {}
        self.new_information = {}
        self.iteration = 0

        self.selection_bias = 0.5

    def init_internal(self, entity):
        super(NewCausalController, self).init_internal(entity)

        # Initialize the node numbering, and other relevant information, for all nodes, 'previous' and 'current'
        self.__create_node_numbering()
        self.__add_experiment_nodes()

    def set_selection_bias(self, bias):
        self.selection_bias = bias

    def add_ignored(self, ignored):
        self.ignored_variables.extend(ignored)

    def __create_node_numbering(self):
        # Create motor_prev nodes and number them
        for action in self.actions:
            self.__add_node(action, self.PREVIOUS)
        # Create sense_prev nodes
        for sense in self.sensory:
            if sense in self.ignored_variables:
                continue
            self.__add_node(sense, self.PREVIOUS)
        # Create action_current nodes
        for action in self.actions:
            self.__add_node(action, self.CURRENT)
        # Create sense_current nodes
        for sense in self.sensory:
            if sense in self.ignored_variables:
                continue
            self.__add_node(sense, self.CURRENT)

        print self.nodes

    def __add_node(self, name, suffix, exploration=True):
        if exploration:
            self.nodes[self.current_number] = name + suffix
            self.node_values[name + suffix] = self.variables[name]
        else:
            self.nodes_exp[self.current_number] = name + suffix
            self.node_values_exp[name + suffix] = self.variables[name]

        self.numberings[name + suffix] = self.current_number

        self.current_number += 1

    def __add_experiment_nodes(self):
        for variable in self.ignored_variables:
            self.__add_node(variable, self.PREVIOUS, exploration=False)
        for variable in self.ignored_variables:
            self.__add_node(variable, self.CURRENT, exploration=False)

    def sense(self, observation):
        # Simply store the information to use later.
        name, value = observation

        self.current_information[name] = value

    def act(self):
        self.iteration += 1

        # 2. Get information (limbs current)
        #    Add current information to memory
        self.new_information = {}
        self.new_information.update(self.current_information)

        # 1. Do babbling
        #    For every motor signal, select a random value
        motor_signals = []
        if self.state == self.STATE_EXPLORATION or self.STATE_EXPERIMENT and self.jpd2 is None:
            motor_signals = self.__select_random_motor_signals()
        elif self.STATE_EXPERIMENT:
            motor_signals = self.__select_maximum_likelihood_motor_signals(("movement", "faster"), self.jpd2)
        print motor_signals

        self.new_information.update(dict(motor_signals))

        if self.state == self.STATE_EXPLORATION:
            self.data.add_entry(self.new_information)
        elif self.state == self.STATE_EXPERIMENT:
            self.data.add_entry(self.new_information)
        self.current_information = {}

        # 3. Compute joint probability distribution
        jpd = self.__compute_joint_probability_distribution(self.node_values)
        jpd2 = None
        if self.state == self.STATE_EXPERIMENT:
            nodes = {}
            nodes.update(self.node_values)
            nodes.update(self.node_values_exp)
            jpd2 = self.__compute_joint_probability_distribution(nodes, min_i=self.exploration_iterations)

        # 4. Learn dependency relations
        #    Check all subsets for independency
        #    Orient resulting network according to constraints (from lower numbers to higher)
        # Create complete network from exploration phase nodes
        self.network = self.__create_complete_network(self.nodes.values())

        # Learn connections from data
        self.__learn_dependency_relations(self.network, jpd)

        if self.state == self.STATE_EXPERIMENT:
            # Also learn the other nodes' edges
            self.__add_nodes_to_network(self.network, self.nodes_exp.values())
            self.__learn_experiment_dependencies(self.network, jpd2)
            self.jpd2 = jpd2

        if self.iteration > self.exploration_iterations:
            self.state = self.STATE_EXPERIMENT

        return motor_signals

    def __select_random_motor_signals(self):
        """
        Hacked for babybot.

        Selects 'still' with probability defined by bias, others with equal rest probability.
        """
        signals = []

        for action in self.actions:
            r = random.random()
            if r < self.selection_bias:
                signals.append((action, "still"))
            elif r < self.selection_bias + (1.0 - self.selection_bias) / float(2):
                signals.append((action, "up"))
            else:
                signals.append((action, "down"))

            # signals.append((action, random.choice(self.actions[action])))

        return signals

    def __select_maximum_likelihood_motor_signals(self, variable, jpd):
        """
        Calculates argmax_CurrentSituation P(Wanted|CurrentSituation).
        """
        # For every assignment of all motor signals (previous)
        assignments = [dict(zip(self.actions, product)) for product in itertools.product(*(self.actions[name] for name in self.actions))]

        arg = None
        max_prob = 0

        for assignment in assignments:
            # Set 'previous' actions to selected actions
            altered = {k + self.PREVIOUS: v for k, v in assignment.items()}
            # Set 'previous' nodes to current situation
            altered.update({k + self.PREVIOUS: v for k, v in self.current_information.items()})

            # Set variable to be calculated as '_current'
            altered_variable = (variable[0] + self.CURRENT, variable[1])

            # Calculate the probability of the 'reinforcer' given the assignment and current information
            prob = self.__calculate_probability_of_given(altered_variable, altered, jpd)

            if prob > max_prob:
                arg = assignment
                max_prob = prob

        if arg is None:
            print "random"
            return self.__select_random_motor_signals()
        else:
            print "probability: {0}".format(max_prob)
            return [(k, v) for k, v in arg.items()]

    def __calculate_probability_of_given(self, node, given, jpd):
        # Calculate P(N|G)
        all_nodes = {node[0]: node[1]}
        all_nodes.update(given)

        p_ng = jpd.partial_prob(all_nodes)
        p_g = jpd.partial_prob(given)

        return 0 if p_g == 0 else p_ng / float(p_g)

    def __compute_joint_probability_distribution(self, variables, min_i=None, max_i=None):
        freq = SparseTable(variables)

        entries = []

        first = 1 if min_i is None else min_i
        last = self.data.last_time() if max_i is None else max_i

        for t_i in range(first, last):
            freq.inc_value(self.data.get_entries_previous_current(t_i))

        n = len(entries)
        if n > 0:
            freq.do_operation(lambda x: x / float(n))

        return easl.utils.Distribution(variables, freq)

    @staticmethod
    def __create_complete_network(nodes):
        c = easl.utils.Graph()
        c.make_complete(nodes)

        return c

    @staticmethod
    def __add_nodes_to_network(network, nodes):
        """
        Adds the new nodes and connects them to all previous nodes
        """
        # Add edges to new nodes
        for node in network.get_nodes():
            for new_node in nodes:
                network.add_node(new_node)
                network.add_edge(node, new_node)

        for x in nodes:
            for y in nodes:
                if x == y:
                    continue

                network.add_edge(x, y)

    def __learn_dependency_relations(self, network, jpd):
        # Check independencies pairwise
        self.__check_independencies(network, jpd)

        # Check all conditional independencies (subsets)
        self.__check_conditional_independencies(network, jpd)

        # Orient edges according to constraints
        self.__orient_edges(network)

    def __learn_experiment_dependencies(self, network, jpd):
        # Check independencies pairwise
        self.__check_independencies(network, jpd, constrained_set=self.nodes_exp.values())

        # Check all conditional independencies (subsets)
        self.__check_conditional_independencies(network, jpd, constrained_set=self.nodes_exp.values())

        # Orient edges according to constraints
        self.__orient_edges(network)

    def __check_independencies(self, graph, jpd, constrained_set=None):
        nodes = graph.get_nodes() if constrained_set is None else constrained_set

        for a in nodes:
            for b in graph.get_connected(a):
                # Check for independence by checking P(A & B) = P(A) * P(B)
                if self.are_independent(a, b, jpd):
                    graph.del_edge(a, b)

    def __check_conditional_independencies(self, graph, jpd, constrained_set=None):
        for n in range(1, len(self.nodes) - 1):
            print "N: {0}".format(n)
            # Select an ordered pair X, Y that are adjacent such that
            # X has n or more other (not Y) adjacencies
            # Select a subset S of size n from X's adjacencies
            # Check if X, Y | S and remove edge between X, Y if so
            nodes = graph.get_nodes() if constrained_set is None else constrained_set

            for u in nodes:
                adjacent = graph.get_connected(u)

                for v in adjacent:
                    if v == u:
                        continue

                    adjacencies = set(graph.get_connected(u))
                    adjacencies.remove(v)

                    # Cardinality of subset should be greater than or equal to n
                    if len(adjacencies) < n:
                        continue

                    for subset in list(itertools.combinations(adjacencies, n)):
                        subset = list(subset)
                        # if X and Y are d-separated, remove X-Y and record S in Sepset(X,Y)
                        if self.are_conditionally_independent(u, v, subset, jpd):
                            # print "({0}, {1})".format(u, v)
                            graph.del_edge(u, v)

    def __orient_edges(self, graph):
        for a, b in graph.get_edges():
            # Check because of possible removal when orienting previously
            if graph.has_edge(a, b) and self.numberings[a] < self.numberings[b]:
                    graph.orient_half(a, b)

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