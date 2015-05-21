__author__ = 'Dennis'

from controller import Controller
import random


class SimpleController(Controller):
    """
    Learns based on operant conditioning.

    Probability of action increases if action is followed
    by reinforcer.
    """
    def __init__(self, rewards):
        """
        Parameters
        ----------
        rewards : [(name, value)]
            List of sensory stimuli that are considered as rewarding.
        Attributes
        ----------
        observations : {name: value}
            Stores current, new, observations.
        action : (name, value)
            The action that was performed last.
        """
        super(SimpleController, self).__init__()

        self.observations = {}
        self.rewards = rewards

        self.action = None
        self.counts = {}

    def init_internal(self, entity):
        super(SimpleController, self).init_internal(entity)

        # select a random action to do
        a = random.choice(self.actions.keys())
        v = random.choice(self.actions[a])

        self.action = (a, v)
        for action in self.actions:
            self.counts[action] = {}
            for value in self.actions[action]:
                self.counts[action][value] = 0

    def sense(self, observation):
        name, value = observation

        self.observations[name] = value

    def act(self):
        action, value = self.action
        # If reward, increase probability
        if self.__got_reward():
            self.counts[action][value] += 1
        # If no reward, decrease probability
        else:
            c = self.counts[action][value] - 1
            self.counts[action][value] = c if c > 0 else 0

        # Select a new action (max probability)
        choices = []
        for action in self.actions:
            for value in self.actions[action]:
                if len(choices) == 0:
                    choices.append((action, value))
                else:
                    a, v = choices[0]
                    # If the count of this action is higher, replace
                    if self.counts[action][value] > self.counts[a][v]:
                        choices = [(action, value)]
                    # Add if same counts
                    elif self.counts[action][value] == self.counts[a][v]:
                        choices.append((action, value))
                    else:
                        continue
        # Only choices with the (same) highest count remain
        # Select one of them at random

        print len(choices)
        self.action = random.choice(choices)
        return [self.action]

    def __got_reward(self):
        for (name, value) in self.rewards:
            if name in self.observations and self.observations[name] == value:
                return True
        return False
