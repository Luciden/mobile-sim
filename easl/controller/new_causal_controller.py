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
    STATE_EXPLORATION = 0
    STATE_EXPERIMENT = 1

    PREVIOUS = "_previous"
    CURRENT = "_current"

    def __init__(self):
        super(NewCausalController, self).__init__(visual=CausalLearningVisual())

        self.state = self.STATE_EXPLORATION
        self.explorations_n = 1000

        # Variables that are ignored in the exploration phase
        self.ignored_variables = []

        self.nodes = {}
        self.node_values = {}
        self.numberings = {}

        self.data = Data()
        self.network = None

        self.current_information = {}

    def init_internal(self, entity):
        super(NewCausalController, self).init_internal(entity)

        self.__create_node_numbering()

    def add_ignored(self, ignored):
        self.ignored_variables.extend(ignored)

    def __create_node_numbering(self):
        current_number = 1
        # Create motor_prev nodes and number them
        for action in self.actions:
            name = action + self.PREVIOUS
            self.nodes[current_number] = name
            self.node_values[name] = self.variables[action]
            self.numberings[name] = current_number
            current_number += 1
        # Create sense_prev nodes
        for sense in self.sensory:
            if sense in self.ignored_variables:
                continue
            name = sense + self.PREVIOUS
            self.nodes[current_number] = name
            self.node_values[name] = self.variables[sense]
            self.numberings[name] = current_number
            current_number += 1
        # Create action_current nodes
        for action in self.actions:
            name = action + self.CURRENT
            self.nodes[current_number] = name
            self.node_values[name] = self.variables[action]
            self.numberings[name] = current_number
            current_number += 1
        # Create sense_current nodes
        for sense in self.sensory:
            if sense in self.ignored_variables:
                continue
            name = sense + self.CURRENT
            self.nodes[current_number] = name
            self.node_values[name] = self.variables[sense]
            self.numberings[name] = current_number
            current_number += 1

        print self.nodes

    def sense(self, observation):
        # Simply store the information to use later.
        name, value = observation

        self.current_information[name] = value

    def act(self):

        if self.state == self.STATE_EXPLORATION:
            return self.__explore()
        elif self.state == self.STATE_EXPERIMENT:
            pass

    def __explore(self):
        """ An iteration in the exploration phase.
        """
        # 1. Do babbling
        #    For every motor signal, select a random value
        motor_signals = self.__select_random_motor_signals()
        print motor_signals

        # 2. Get information (limbs current)
        #    Add current information to memory
        new_information = {}
        new_information.update(self.current_information)
        new_information.update(motor_signals)

        self.data.add_entry(new_information)
        self.current_information = {}

        # 3. Compute joint probability distribution
        jpd = self.__compute_joint_probability_distribution(self.node_values)
        print "computed"

        # 4. Learn dependency relations
        #    Check all subsets for independency
        #    Orient resulting network according to constraints (from lower numbers to higher)
        self.network = self.__learn_dependency_relations(jpd)

        return motor_signals

    def __select_random_motor_signals(self):
        signals = []

        for action in self.actions:
            signals.append((action, random.choice(self.actions[action])))

        return signals

    def __compute_joint_probability_distribution(self, variables):
        freq = SparseTable(variables)

        entries = []

        for t_i in range(1, self.data.last_time()):
            freq.inc_value(self.data.get_entries_previous_current(t_i))

        n = len(entries)
        if n > 0:
            freq.do_operation(lambda x: x / float(n))

        return easl.utils.Distribution(variables, freq)

    def __learn_dependency_relations(self, jpd):
        # Create complete graph
        c = easl.utils.Graph()
        c.make_complete(self.nodes.values())

        # Check independencies pairwise
        self.__check_independencies(c, jpd)

        # Check all conditional independencies (subsets)
        self.__check_conditional_independencies(c, jpd)

        # Orient edges according to constraints
        self.__orient_edges(c)

        return c

    def __check_independencies(self, graph, jpd):
        for a in graph.get_nodes():
            for b in graph.get_connected(a):
                # Check for independence by checking P(A & B) = P(A) * P(B)
                if self.are_independent(a, b, jpd):
                    graph.del_edge(a, b)

    def __check_conditional_independencies(self, graph, jpd):
        for n in range(1, len(self.nodes) - 1):
            print "N: {0}".format(n)
            # Select an ordered pair X, Y that are adjacent such that
            # X has n or more other (not Y) adjacencies
            # Select a subset S of size n from X's adjacencies
            # Check if X, Y | S and remove edge between X, Y if so
            for u in graph.get_nodes():
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
            if graph.has_edge(a, b):
                if self.numberings[a] < self.numberings[b]:
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