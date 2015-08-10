__author__ = 'Dennis'

import easl
from easl.utils import SparseTable
from easl.utils import SparseConditionalTable
from controller import Controller
from easl import visualize

import random
from copy import deepcopy


class Data(object):
    def __init__(self):
        self.entries = []

    def add_entry(self, vals):
        self.entries.append(deepcopy(vals))

    def get_entries_at_time(self, time):
        return self.entries[time]

    def get_entries_previous_current(self, time, variables, motor):
        if time >= len(self.entries) or time - 2 < 0:
            return {}

        past = self.entries[time - 2]
        previous = self.entries[time - 1]
        current = self.entries[time]

        previous_entries_motor = {x + NewCausalController.PREVIOUS: y
                                  for (x, y) in past.iteritems()
                                  if x in motor and x + NewCausalController.PREVIOUS in variables}
        current_entries_motor = {x + NewCausalController.CURRENT: y
                                 for (x, y) in previous.iteritems()
                                 if x in motor and x + NewCausalController.CURRENT in variables}
        previous_entries_sensor = {x + NewCausalController.PREVIOUS: y
                                   for (x, y) in previous.iteritems()
                                   if x not in motor and x + NewCausalController.PREVIOUS in variables}
        current_entries_sensor = {x + NewCausalController.CURRENT: y
                                  for (x, y) in current.iteritems()
                                  if x not in motor and x + NewCausalController.CURRENT in variables}

        entries = {}
        entries.update(previous_entries_motor)
        entries.update(current_entries_motor)
        entries.update(previous_entries_sensor)
        entries.update(current_entries_sensor)

        return entries

    def last_time(self):
        return len(self.entries) - 1

    def get_latest_entry(self, offset=0):
        return self.entries[-1 - offset]


class DistributionComputer(object):
    @staticmethod
    def compute_frequency_table(variables, data, motor):
        """
        Parameters
        ----------
        variables : [string]
        data : Data
        motor : [string]
        """
        freq = SparseTable(variables)

        first = 2
        last = data.last_time() + 1

        n = 0

        for t_i in range(first, last):
            n += 1
            freq.inc_value(data.get_entries_previous_current(t_i, variables.keys(), motor))

        return freq, n

    @staticmethod
    def compute_joint_probability_distribution(variables, data, motor):
        freq, n = DistributionComputer.compute_frequency_table(variables, data, motor)

        if n > 0:
            freq.do_operation(lambda x: x / float(n))

        return easl.utils.Distribution(variables, freq)

    @staticmethod
    def compute_conditional_probability_distribution(variables, data, motor, conditioned):
        """
        """
        freq, n = DistributionComputer.compute_frequency_table(variables, data, motor)

        # Total number of occurences with only exploration variables
        totals = SparseTable({k: v for k, v in variables.iteritems()
                              if k not in conditioned})

        jpd = SparseConditionalTable(variables, {k: v for k, v in variables.iteritems() if k not in conditioned})

        # Make conditional on exploration variables
        # i.e. divide by total number of
        for entry in freq.get_nonzero_entries():
            filtered = {k: v for k, v in entry.iteritems() if k not in conditioned}
            # Add the values to increase the total
            totals.set_value(filtered, totals.get_value(filtered) + freq.get_value(entry))

        # Make conditional table by dividing by subtotals
        for entry in freq.get_nonzero_entries():
            filtered = {k: v for k, v in entry.iteritems() if k not in conditioned}

            # P(M|R) = F(M&R) / F(R)
            f_r = float(totals.get_value(filtered))
            jpd.set_value(entry, 0 if f_r == 0 else freq.get_value(entry) / f_r)

        return jpd


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
        self.exploration_iterations = 50

        self.rewards = {}

        self.motor_signal_valuation = lambda x: 1.0
        self.motor_signal_bias = 1.0

        self.ignored_variables = []
        self.considered_signals = []
        self.considered_sensory = []

        self.numberings = {}

        # Variables in the exploration phase
        self.nodes = {}
        self.node_values = {}

        # Variables added after the exploration phase
        self.nodes_exp = {}
        self.node_values_exp = {}

        # All variables
        self.nodes_all = {}
        self.node_values_all = {}

        self.node_values_cond_motor = {}
        self.node_values_cond_limb = {}

        self.node_values_limb = {}
        self.node_values_motor = {}

        self.current_number = 1

        self.data = Data()
        self.data2 = Data()
        self.network = None
        self.jpd = None
        # P(limb|motor)
        self.jpd2 = None
        # P(mobile|limb)
        self.jpd3 = None

        self.current_information = {}
        self.new_information = {}
        self.iteration = 0

        self.selection_bias = 0.5
        self.calculate_once = True

        self.epsilon = 0.2

    def init_internal(self, entity):
        super(NewCausalController, self).init_internal(entity)

        # Initialize the node numbering, and other relevant information, for all nodes, 'previous' and 'current'
        self.__create_node_numbering()
        self.__add_experiment_nodes()

        print self.nodes_all

    def set_selection_bias(self, bias):
        self.selection_bias = bias

    def set_motor_signal_bias(self, valuation, bias):
        self.motor_signal_valuation = valuation
        self.motor_signal_bias = bias

    def set_rewards(self, vals):
        self.rewards.update(vals)

    def add_ignored(self, ignored):
        self.ignored_variables.extend(ignored)

    def set_considered_signals(self, signals):
        self.considered_signals = signals

    def set_considered_sensory(self, sensory):
        self.considered_sensory = sensory

    def __create_node_numbering(self):
        # Create motor_prev nodes and number them
        for action in self.actions:
            if action not in self.considered_signals:
                continue
            self.__add_node(action, self.PREVIOUS)
        # Create sense_prev nodes
        for sense in self.sensory:
            if sense in self.ignored_variables:
                continue
            if sense not in self.considered_sensory:
                continue
            self.__add_node(sense, self.PREVIOUS)
        # Create action_current nodes
        for action in self.actions:
            if action not in self.considered_signals:
                continue
            self.__add_node(action, self.CURRENT)
        # Create sense_current nodes
        for sense in self.sensory:
            if sense in self.ignored_variables:
                continue
            self.__add_node(sense, self.CURRENT)

    def __add_node(self, name, suffix, exploration=True):
        node = name + suffix

        if exploration:
            self.nodes[self.current_number] = node
            self.node_values[node] = self.variables[name]
        else:
            self.nodes_exp[self.current_number] = node
            self.node_values_exp[node] = self.variables[name]

        self.numberings[node] = self.current_number

        self.nodes_all[self.current_number] = node
        self.node_values_all[node] = self.variables[name]

        if name in self.actions.keys():
            self.node_values_cond_motor[node] = self.variables[name]

            self.node_values_motor[node] = self.variables[name]
        elif name in self.ignored_variables:
            self.node_values_cond_limb[node] = self.variables[name]
        else:
            self.node_values_cond_motor[node] = self.variables[name]
            self.node_values_cond_limb[node] = self.variables[name]

            self.node_values_limb[node] = self.variables[name]

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

        if self.iteration == self.exploration_iterations:
            print "Exploration Complete"
            # Calculate the probability table from the exploration data once
            self.jpd = DistributionComputer.compute_joint_probability_distribution(self.node_values, self.data, self.actions.keys())
            self.jpd2 = DistributionComputer.compute_conditional_probability_distribution(self.node_values_cond_motor,
                                                                                          self.data,
                                                                                          self.actions.keys(),
                                                                                          self.node_values_limb.keys())

            # Transfer data so new actions can be calculated immediately
            self.data2.add_entry(self.data.get_latest_entry(2))
            self.data2.add_entry(self.data.get_latest_entry(1))
            self.data2.add_entry(self.data.get_latest_entry())

            self.state = self.STATE_EXPERIMENT

        motor_signals = []

        if self.state == self.STATE_EXPLORATION:
            # Motor babbling; select random motor signals
            motor_signals = self.__select_random_motor_signals()
        elif self.state == self.STATE_EXPERIMENT:
            # Select signals by maximum likelihood from collected (all) data
            self.jpd3 = DistributionComputer.compute_conditional_probability_distribution(self.node_values_cond_limb,
                                                                                          self.data2,
                                                                                          self.actions.keys(),
                                                                                          self.node_values_exp.keys())

            r = random.random()
            if r < self.epsilon:
                print "Selecting randomly"
                motor_signals = self.__select_random_motor_signals()
            else:
                motor_signals = self.__select_maximum()

        self.new_information = {}
        self.new_information.update(self.current_information)
        self.new_information.update(dict(motor_signals))

        if self.state == self.STATE_EXPLORATION:
            self.data.add_entry(self.new_information)
        elif self.state == self.STATE_EXPERIMENT:
            self.data2.add_entry(self.new_information)

        # Reset for new iteration
        self.current_information = {}

        return motor_signals

    def __select_maximum(self):
        # Select the combination of motor signals that maximizes probability
        constant = {}

        # Set latest selected motor signals as previous motor signals
        for signal in self.actions.keys():
            constant[signal + self.PREVIOUS] = self.data2.get_latest_entry()[signal]

        # Set latest known limb positions as previous limb positions
        for signal in self.sensory.keys():
            if signal in self.ignored_variables:
                continue

            constant[signal + self.PREVIOUS] = self.current_information[signal]

        # Set latest known mobile thing as previous mobile thing
        for signal in self.ignored_variables:
            constant[signal + self.PREVIOUS] = self.current_information[signal]

        for signal in self.rewards:
            constant[signal + self.CURRENT] = self.rewards[signal]

        # Get maximum probability by checking all possible combinations of motor signals
        max_valuation = 0.0
        max_combinations = []
        for combination in self.all_possibilities({k: v for k, v in self.actions.iteritems() if k in self.considered_signals}):
        #for combination in self.__subset_possibilities(self.actions, 1):
            combination.update({k: "still" for k in self.actions.keys() if k not in self.considered_signals})

            assignment = {}
            assignment.update(constant)
            assignment.update({k + self.CURRENT: v for k, v in combination.iteritems()})

            total = 0.0
            if self.__are_all_nodes(assignment):
                total = self.jpd2.get_value(assignment)
            else:
                # Marginalize over current 'limb positions'
                # P(X|Y = y) = \sum_A P(X,A,Y = y) * P(A,Y = y) / \sum_A P(A,Y = y) * P(Y = y)
                for sensories in self.all_possibilities(self.sensory):
                    sensory_assignment = {k + self.CURRENT: v for k, v in sensories.iteritems()
                                          if k not in self.rewards.keys()}
                    total_assignment = {}
                    total_assignment.update(assignment)
                    total_assignment.update(sensory_assignment)

                    # Filter
                    total_assignment = {k: v for k, v in total_assignment.iteritems()
                                        if k in self.node_values_all.keys()}

                    motor_assignment = {k: v for k, v in total_assignment.iteritems() if k in self.node_values_cond_motor.keys()}
                    limb_assignment = {k: v for k, v in total_assignment.iteritems() if k in self.node_values_cond_limb.keys()}

                    pl_m_assignment = {}
                    pl_m_assignment.update({k: v for k, v in assignment.iteritems() if k in self.node_values_motor.keys()})
                    pl_m_assignment.update({k: v for k, v in motor_assignment.iteritems() if k in self.node_values_motor.keys()})

                    if self.jpd2.has_data(pl_m_assignment):
                        pl_m = self.jpd2.get_value(motor_assignment)
                    else:
                        pl_m = 1 / float(81)

                    # if all pmm_l are zero for all mm, then give a default one
                    if self.jpd3.has_data({k: v for k, v in limb_assignment.iteritems() if k in self.node_values_limb.keys()}):
                        pmm_l = self.jpd3.get_value(limb_assignment)
                    else:
                        pmm_l = 1 / float(16)

                    total += pl_m * pmm_l
                    #print "total {0} = {1} * {2}".format(total, pl_m, pmm_l)

            valuation = total * self.motor_signal_valuation(combination)

            if valuation == max_valuation:
                max_combinations.append(combination)
            elif valuation > max_valuation:
                print "Updated"
                max_valuation = valuation
                max_combinations = []
                max_combinations.append(combination)

        if len(max_combinations) is not 0:
            max_combination = random.choice(max_combinations)
            print "Selected {0} with probability {1}".format(max_combination, max_valuation)
            return [(k, v) for k, v in max_combination.iteritems()]
        else:
            return None

    def __are_all_nodes(self, assignment):
        for node in self.node_values_all.keys():
            if node not in assignment.keys():
                return False
        return True

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

        return signals

    @staticmethod
    def __subset_possibilities(variables, n):
        possibilities = []

        for v in variables:
            for val in variables[v]:
                if val == "still":
                    continue

                possibility = {v: val}
                for u in variables:
                    if u == v:
                        continue

                    possibility[u] = "still"

                possibilities.append(possibility)

        return possibilities
