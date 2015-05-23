__author__ = 'Dennis'

from controller import Controller
import random


class LearningRule(object):
    @staticmethod
    def update_counts(counts, action, has_reward):
        """
        Describes how the counts/probability changes given that an action was
        contiguous with a reward.

        Changes counts as a side-effect without returning anything.

        Parameters
        ----------
        counts : {name: {value: int}}
            See SimpleController.counts.
        action : (name, value)
        has_reward : bool
            True if the reward is present, False otherwise.
        """
        raise NotImplementedError("The interface method should be overridden.")

    @staticmethod
    def select_action(counts):
        """
        Parameters
        ----------
        counts : {name: {value: int}}

        Returns
        -------
        action : (name, value)
        """
        raise NotImplementedError("The interface method should be overridden.")


class SimpleLearningRule(LearningRule):
    @staticmethod
    def update_counts(counts, action, has_reward):
        a, v = action
        # If the reward is present, increase the probability of selecting the
        # action.
        if has_reward:
            counts[a][v] += 1
        # If not, decrease the probability of selecting the action again.
        else:
            counts[a][v] = max(0, counts[a][v] - 1)

    @staticmethod
    def select_action(counts):
        choices = []

        # Find actions with maximum count
        for action in counts:
            for value in counts[action]:
                if len(choices) == 0:
                    choices.append((action, value))
                else:
                    a, v = choices[0]
                    # If the count of the new action is the same as the already
                    # found actions, add it
                    if counts[action][value] == counts[a][v]:
                        choices.append((action, value))
                    # If the count of the new action is higher, replace
                    elif counts[action][value] > counts[a][v]:
                        choices = [(action, value)]
                    # Count is lower, so skip
                    else:
                        continue

        # If there are multiple choices, select one at random
        print len(choices)
        return random.choice(choices)


class BetterLearningRule(LearningRule):
    @staticmethod
    def update_counts(counts, action, has_reward):
        a, v = action
        if has_reward:
            # Increase the probability of choosing the specific action again
            counts[a][v] += 1
            # Also increase the probability of all actions of this name
            for value in counts[a]:
                counts[a][value] += 1
        else:
            # Decrease probability of choosing this action
            counts[a][v] = max(0, counts[a][v] - 1)
            # Also decrease probability of choosing other actions of same type
            for value in counts[a]:
                counts[a][value] = max(0, counts[a][value] - 1)

    @staticmethod
    def select_action(counts):
        return SimpleLearningRule.select_action(counts)


class SimpleController(Controller):
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
        super(SimpleController, self).__init__()

        self.rule = BetterLearningRule()

        self.observations = {}
        self.rewards = rewards

        self.action = None
        self.counts = {}

    def init_internal(self, entity):
        super(SimpleController, self).init_internal(entity)

        for action in self.actions:
            self.counts[action] = {}
            for value in self.actions[action]:
                self.counts[action][value] = 0

        # Select a random action to do (random because all counts are 0)
        self.action = self.rule.select_action(self.counts)

    def sense(self, observation):
        name, value = observation

        self.observations[name] = value

    def act(self):
        # Change the counts according to selected action and whether a
        # reward is present
        self.rule.update_counts(self.counts, self.action, self.__got_reward())

        # Select a new action (max probability)
        return [self.rule.select_action(self.counts)]

    def __got_reward(self):
        for (name, value) in self.rewards:
            if name in self.observations and self.observations[name] == value:
                return True
        return False
