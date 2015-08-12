from unittest import TestCase
from easl.utils import Distribution
from easl.mechanisms import CausalLearningMechanism

__author__ = 'Dennis'


class TestCausalLearningAgent(TestCase):
    def test_conditional_probability(self):
        ab = Distribution({"Coin1": ["heads", "tails"], "Coin2": ["heads", "tails"]})

        ab.set_prob({"Coin1": "heads", "Coin2": "heads"}, 0.25)
        ab.set_prob({"Coin1": "heads", "Coin2": "tails"}, 0.25)
        ab.set_prob({"Coin1": "tails", "Coin2": "heads"}, 0.25)
        ab.set_prob({"Coin1": "tails", "Coin2": "tails"}, 0.25)

        self.assertEqual(0.5, CausalLearningMechanism.conditional_probability(["Coin1", "Coin2"], ab, "heads", "tails"))

    def test_are_independent_independent(self):
        d = Distribution({"Coin1": ["heads", "tails"], "Coin2": ["heads", "tails"]})

        d.set_prob({"Coin1": "heads", "Coin2": "heads"}, 0.25)
        d.set_prob({"Coin1": "heads", "Coin2": "tails"}, 0.25)
        d.set_prob({"Coin1": "tails", "Coin2": "heads"}, 0.25)
        d.set_prob({"Coin1": "tails", "Coin2": "tails"}, 0.25)

        self.assertTrue(CausalLearningMechanism.are_independent("Coin1", "Coin2", d))

    def test_are_independent_dependent(self):
        d = Distribution({"Weather": ["clear", "cloudy"], "Temperature": ["warm", "cold"]})

        d.set_prob({"Weather": "clear", "Temperature": "warm"}, 0.4)
        d.set_prob({"Weather": "clear", "Temperature": "cold"}, 0.2)
        d.set_prob({"Weather": "cloudy", "Temperature": "warm"}, 0.1)
        d.set_prob({"Weather": "cloudy", "Temperature": "cold"}, 0.3)

        self.assertFalse(CausalLearningMechanism.are_independent("Weather", "Temperature", d))

    def test_are_conditionally_independent3(self):
        d = Distribution({"Coin1": ["heads", "tails"], "Coin2": ["heads", "tails"], "Coin3": ["heads", "tails"]})

        d.set_prob({"Coin1": "heads", "Coin2": "heads", "Coin3": "heads"}, 0.125)
        d.set_prob({"Coin1": "heads", "Coin2": "heads", "Coin3": "tails"}, 0.125)
        d.set_prob({"Coin1": "heads", "Coin2": "tails", "Coin3": "heads"}, 0.125)
        d.set_prob({"Coin1": "heads", "Coin2": "tails", "Coin3": "tails"}, 0.125)
        d.set_prob({"Coin1": "tails", "Coin2": "heads", "Coin3": "heads"}, 0.125)
        d.set_prob({"Coin1": "tails", "Coin2": "heads", "Coin3": "tails"}, 0.125)
        d.set_prob({"Coin1": "tails", "Coin2": "tails", "Coin3": "heads"}, 0.125)
        d.set_prob({"Coin1": "tails", "Coin2": "tails", "Coin3": "tails"}, 0.125)

        self.assertTrue(CausalLearningMechanism.are_conditionally_independent("Coin1", "Coin2", ["Coin3"], d))

    def test_are_conditionally_independent4(self):
        d = Distribution({"Coin1": ["heads", "tails"],
                          "Coin2": ["heads", "tails"],
                          "Coin3": ["heads", "tails"],
                          "Coin4": ["heads", "tails"]})

        d.set_prob({"Coin1": "heads", "Coin2": "heads", "Coin3": "heads", "Coin4": "heads"}, 0.0625)
        d.set_prob({"Coin1": "heads", "Coin2": "heads", "Coin3": "heads", "Coin4": "tails"}, 0.0625)
        d.set_prob({"Coin1": "heads", "Coin2": "heads", "Coin3": "tails", "Coin4": "heads"}, 0.0625)
        d.set_prob({"Coin1": "heads", "Coin2": "heads", "Coin3": "tails", "Coin4": "tails"}, 0.0625)
        d.set_prob({"Coin1": "heads", "Coin2": "tails", "Coin3": "heads", "Coin4": "heads"}, 0.0625)
        d.set_prob({"Coin1": "heads", "Coin2": "tails", "Coin3": "heads", "Coin4": "tails"}, 0.0625)
        d.set_prob({"Coin1": "heads", "Coin2": "tails", "Coin3": "tails", "Coin4": "heads"}, 0.0625)
        d.set_prob({"Coin1": "heads", "Coin2": "tails", "Coin3": "tails", "Coin4": "tails"}, 0.0625)
        d.set_prob({"Coin1": "tails", "Coin2": "heads", "Coin3": "heads", "Coin4": "heads"}, 0.0625)
        d.set_prob({"Coin1": "tails", "Coin2": "heads", "Coin3": "heads", "Coin4": "tails"}, 0.0625)
        d.set_prob({"Coin1": "tails", "Coin2": "heads", "Coin3": "tails", "Coin4": "heads"}, 0.0625)
        d.set_prob({"Coin1": "tails", "Coin2": "heads", "Coin3": "tails", "Coin4": "tails"}, 0.0625)
        d.set_prob({"Coin1": "tails", "Coin2": "tails", "Coin3": "heads", "Coin4": "heads"}, 0.0625)
        d.set_prob({"Coin1": "tails", "Coin2": "tails", "Coin3": "heads", "Coin4": "tails"}, 0.0625)
        d.set_prob({"Coin1": "tails", "Coin2": "tails", "Coin3": "tails", "Coin4": "heads"}, 0.0625)
        d.set_prob({"Coin1": "tails", "Coin2": "tails", "Coin3": "tails", "Coin4": "tails"}, 0.0625)

        self.assertTrue(CausalLearningMechanism.are_conditionally_independent("Coin1", "Coin2", ["Coin3", "Coin4"], d))

    def test_are_conditionally_independent_not_independent(self):
        d = Distribution({"Coin1": ["heads", "tails"], "Coin2": ["heads", "tails"], "Coin3": ["heads", "tails"]})

        d.set_prob({"Coin1": "heads", "Coin2": "heads", "Coin3": "heads"}, 0.5)
        d.set_prob({"Coin1": "heads", "Coin2": "heads", "Coin3": "tails"}, 0.1)
        d.set_prob({"Coin1": "heads", "Coin2": "tails", "Coin3": "heads"}, 0.2)
        d.set_prob({"Coin1": "heads", "Coin2": "tails", "Coin3": "tails"}, 0.3)
        d.set_prob({"Coin1": "tails", "Coin2": "heads", "Coin3": "heads"}, 0.6)
        d.set_prob({"Coin1": "tails", "Coin2": "heads", "Coin3": "tails"}, 0.7)
        d.set_prob({"Coin1": "tails", "Coin2": "tails", "Coin3": "heads"}, 0.8)
        d.set_prob({"Coin1": "tails", "Coin2": "tails", "Coin3": "tails"}, 0.9)

        self.assertFalse(CausalLearningMechanism.are_conditionally_independent("Coin1", "Coin2", ["Coin3"], d))
