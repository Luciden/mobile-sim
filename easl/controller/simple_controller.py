__author__ = 'Dennis'

from controller import Controller
from easl.visualize import *
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


class ActionSelection(object):
    @staticmethod
    def select_action(counts):
        """Select an action with the highest count.

        When multiple actions have the same highest count, select one of those
        at random.

        Parameters
        ----------
        counts : {name: {value: int}}

        Returns
        -------
        action : (name, value)
        """
        raise NotImplementedError("The interface method should be overridden.")


class SimpleLearningRule(LearningRule):
    """
    Increments count of an action by a fixed amount if and only if the
    action was followed by a reward.
    Decrements count of an action if and only if it was not followed by
    a reward.
    """
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


class SimpleSelection(ActionSelection):
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
    """Uses information that some actions might be related.

    Whenever an action is followed by a reward, it is incremented by a fixed
    amount A, and actions sharing the same action symbol are incremented by
    a fixed amount B.
    Whenever an action is not followed by a reward, its count is decremented
    by a fixed amount C, and actions sharing the same action symbol are
    decremented by a fixed amount D.
    """
    @staticmethod
    def update_counts(counts, action, has_reward):
        a, v = action
        if has_reward:
            # Increase the probability of choosing the specific action again
            counts[a][v] += 3
            # Also increase the probability of all other actions of this type
            for value in counts[a]:
                if value == v:
                    continue
                counts[a][value] += 2
        else:
            # Decrease probability of choosing this action
            counts[a][v] = max(0, counts[a][v] - 2)
            # Also decrease probability of choosing other actions of same type
            for value in counts[a]:
                if value == v:
                    continue
                counts[a][value] = max(0, counts[a][value] - 1)


class RouletteWheelSelection(ActionSelection):
    @staticmethod
    def select_action(counts):
        # Get total size of wheel
        total = 0
        for a in counts:
            for v in counts[a]:
                total += counts[a][v]

        # Create structure that has for every upper threshold
        # the selection
        cumulative = 0
        wheel = {}
        for a in counts:
            for v in counts[a]:
                c = counts[a][v]
                if c == 0:
                    continue
                cumulative += c
                wheel[cumulative/float(total)] = (a, v)

        # Generate random number between 0 and 1
        r = random.random()

        # Find item that has number fall between previous upper threshold and own threshold
        previous = 0.0
        for p in sorted(wheel):
            # When the wheel doesn't stop at this section
            if previous <= r < p:
                return wheel[p]


class SimpleVisual(Visual):
    @staticmethod
    def visualize(self):
        tree = Tree("counts", self.counts)

        group = Group("simple")
        group.add_element(tree)

        return group


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
        self.visual = SimpleVisual()

        self.rule = BetterLearningRule()
        self.selection = RouletteWheelSelection()

        self.observations = {}
        self.rewards = rewards

        self.action = None
        self.counts = {}

    def init_internal(self, entity):
        super(SimpleController, self).init_internal(entity)

        for action in self.actions:
            self.counts[action] = {}
            for value in self.actions[action]:
                self.counts[action][value] = 5

        # Select a random action to do (random because all counts are 0)
        self.action = self.selection.select_action(self.counts)

    def sense(self, observation):
        name, value = observation

        self.observations[name] = value

    def act(self):
        # Change the counts according to selected action and whether a
        # reward is present
        self.rule.update_counts(self.counts, self.action, self.__got_reward())

        # Select a new action (max probability)
        self.action = self.selection.select_action(self.counts)
        if self.action is None:
            a = random.choice(self.actions.keys())
            v = random.choice(self.actions[a])

            self.action = (a, v)

        return [self.action]

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
