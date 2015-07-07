__author__ = 'Dennis'

from controller import Controller
from easl import *
from easl.visualize import *
import random


class NewSimpleVisual(Visual):
    @staticmethod
    def visualize(self):
        trees = {}
        for action in self.actions:
            trees[action] = {}
            for value in self.actions[action]:
                trees[action][value] = 0.0

        for combination in self.all_possibilities(self.actions):
            for k, v in combination.iteritems():
                trees[k][v] += self.probabilities.get_value(combination)

        group = Group("simple")
        for action in trees:
            group.add_element(Tree(action, trees[action]))

        return group


class NewSimpleController(Controller):
    """
    Learns based on operant conditioning.

    Probability of action increases if action is followed
    by reinforcer.

    Attributes
    ----------
    observations : {name: value}
        Stores current, new, observations.
    rule : LearningRule
    action : (name, value)
        The action that was performed last.
    counts : {name: {value: int}}
        Maintains a count for any action/value pair.
    rewards : [(name, value)]
        List of sensory stimuli that are considered as rewarding.
    """
    def __init__(self, rewards):
        """
        Parameters
        ----------
        rewards : [(name, value)]
            List of sensory stimuli that are considered as rewarding.
        """
        super(NewSimpleController, self).__init__()
        self.visual = NewSimpleVisual()

        self.observations = {}
        self.rewards = rewards

        self.action = None
        self.probabilities = None

        self.motor_signal_valuation = lambda x: 1.0
        self.motor_signal_bias = 1.0

        self.delta = 0.1
        self.max_probability = 0.9
        self.min_probability = 0.01

    def init_internal(self, entity):
        super(NewSimpleController, self).init_internal(entity)

        # Initialize the probability table
        self.probabilities = utils.FullTable(self.actions)
        # Initialize with uniform distribution
        # Count total possibilities
        n = 0
        for combination in self.all_possibilities(self.actions):
            n += 1

        p = 1 / float(n)
        self.probabilities.do_operation(lambda x: p)
        print self.probabilities.table

    def set_motor_signal_bias(self, valuation, bias):
        self.motor_signal_valuation = valuation
        self.motor_signal_bias = bias

    def sense(self, observation):
        name, value = observation

        self.observations[name] = value

    def act(self):
        # Change the counts according to selected action and whether a
        # reward is present
        if self.action is not None:
            self.__update_probabilities(self.__got_reward())

        # Select a new action (max probability)
        self.action = self.__select_action()

        return [(x, y) for x, y in self.action.iteritems()]

    def __select_action(self):
        """
        Select the combination of actions with the maximum likelihood of
        resulting in a reward.
        """
        values = []
        total = 0.0

        possibilities = self.all_possibilities(self.actions)

        for combination in possibilities:
            v = self.probabilities.get_value(combination) * self.motor_signal_bias + (1.0 - self.motor_signal_bias) * self.motor_signal_valuation(combination)
            values.append(v)

            total += v

        r = random.random()

        cumulative = 0.0
        for i in range(len(values)):
            cumulative += values[i]

            if cumulative >= r:
                print "Selected {0}, which had probability {1}".format(possibilities[i], values[i] / float(total))
                return possibilities[i]

    def __update_probabilities(self, rewarded):
        old = self.probabilities.get_value(self.action)
        new = 0

        # Change probability of one particular
        if rewarded:
            new = min(old + self.delta, self.max_probability)
        else:
            new = max(old - self.delta, self.min_probability)

        self.probabilities.set_value(self.action, new)

        # Renormalize
        self.probabilities.do_operation(lambda x: x / float(1.0 + (new - old)))

        print "Old: {0}, New {1}, Normalized {2}".format(old, new, self.probabilities.get_value(self.action))

    def __got_reward(self):
        """
        Returns
        -------
        got_reward : boolean
            True if a rewarding stimulus is present, False otherwise.
        """
        for (name, value) in self.rewards:
            if name in self.observations and self.observations[name] == value:
                return True
        return False
