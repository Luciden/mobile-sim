from unittest import TestCase
from easl.utils import *

__author__ = 'Dennis'


class TestDistribution(TestCase):
    def test_equals_equal(self):
        d = Distribution({"Coin1": ["heads", "tails"], "Coin2": ["heads", "tails"]})

        d.set_prob({"Coin1": "heads", "Coin2": "heads"}, 0.25)
        d.set_prob({"Coin1": "heads", "Coin2": "tails"}, 0.25)
        d.set_prob({"Coin1": "tails", "Coin2": "heads"}, 0.25)
        d.set_prob({"Coin1": "tails", "Coin2": "tails"}, 0.25)

        e = Distribution({"Coin1": ["heads", "tails"], "Coin2": ["heads", "tails"]})

        e.set_prob({"Coin1": "heads", "Coin2": "heads"}, 0.25)
        e.set_prob({"Coin1": "heads", "Coin2": "tails"}, 0.25)
        e.set_prob({"Coin1": "tails", "Coin2": "heads"}, 0.25)
        e.set_prob({"Coin1": "tails", "Coin2": "tails"}, 0.25)

        self.assertTrue(d == e)

    def test_equals_not_equal(self):
        d = Distribution({"Coin1": ["heads", "tails"], "Coin2": ["heads", "tails"]})

        d.set_prob({"Coin1": "heads", "Coin2": "heads"}, 0.25)
        d.set_prob({"Coin1": "heads", "Coin2": "tails"}, 0.25)
        d.set_prob({"Coin1": "tails", "Coin2": "heads"}, 0.25)
        d.set_prob({"Coin1": "tails", "Coin2": "tails"}, 0.25)

        e = Distribution({"Coin1": ["heads", "tails"], "Coin2": ["heads", "tails"]})

        e.set_prob({"Coin1": "heads", "Coin2": "heads"}, 0.15)
        e.set_prob({"Coin1": "heads", "Coin2": "tails"}, 0.15)
        e.set_prob({"Coin1": "tails", "Coin2": "heads"}, 0.15)
        e.set_prob({"Coin1": "tails", "Coin2": "tails"}, 0.15)

        self.assertFalse(d == e)

    def test_equals_different_variables(self):
        d = Distribution({"Coin1": ["heads", "tails"]})

        e = Distribution({"Coin2": ["heads", "tails"]})

        self.assertFalse(d.__eq__(e))

    def test_equals_different_values(self):
        d = Distribution({"Coin1": ["heads", "tails"]})

        e = Distribution({"Coin1": ["up", "down"]})

    def test_set_prob_normal(self):
        d = Distribution({"Coin1": ["heads", "tails"], "Coin2": ["heads", "tails"]})

        d.set_prob({"Coin1": "heads", "Coin2": "heads"}, 0.25)

        self.assertEqual(0.25, d.table["heads"]["heads"])

    #def test_set_prob_wrong_index(self):
    #    d = Distribution({"Coin1": ["heads", "tails"], "Coin2": ["heads", "tails"]})

    #    self.assertRaises(IndexError, d.set_prob, {"Rain": "yes"}, 1)

    def test_prob_normal(self):
        d = Distribution({"Coin1": ["heads", "tails"], "Coin2": ["heads", "tails"]})

        d.set_prob({"Coin1": "heads", "Coin2": "heads"}, 0.25)
        d.set_prob({"Coin1": "heads", "Coin2": "tails"}, 0.25)
        d.set_prob({"Coin1": "tails", "Coin2": "heads"}, 0.25)
        d.set_prob({"Coin1": "tails", "Coin2": "tails"}, 0.25)

        self.assertEqual(0.25, d.prob({"Coin1": "heads", "Coin2": "tails"}))

    def test_single_prob_normal(self):
        d = Distribution({"Coin1": ["heads", "tails"], "Coin2": ["heads", "tails"], "Coin3": ["heads", "tails"]})

        d.set_prob({"Coin1": "heads", "Coin2": "heads", "Coin3": "heads"}, 0.125)
        d.set_prob({"Coin1": "heads", "Coin2": "heads", "Coin3": "tails"}, 0.125)
        d.set_prob({"Coin1": "heads", "Coin2": "tails", "Coin3": "heads"}, 0.125)
        d.set_prob({"Coin1": "heads", "Coin2": "tails", "Coin3": "tails"}, 0.125)
        d.set_prob({"Coin1": "tails", "Coin2": "heads", "Coin3": "heads"}, 0.125)
        d.set_prob({"Coin1": "tails", "Coin2": "heads", "Coin3": "tails"}, 0.125)
        d.set_prob({"Coin1": "tails", "Coin2": "tails", "Coin3": "heads"}, 0.125)
        d.set_prob({"Coin1": "tails", "Coin2": "tails", "Coin3": "tails"}, 0.125)

        self.assertEqual(0.5, d.single_prob("Coin1", "heads"))
        self.assertEqual(0.5, d.single_prob("Coin2", "heads"))
        self.assertEqual(0.5, d.single_prob("Coin3", "heads"))

    def test_partial_prob_normal(self):
        d = Distribution({"Coin1": ["heads", "tails"], "Coin2": ["heads", "tails"], "Coin3": ["heads", "tails"]})

        d.set_prob({"Coin1": "heads", "Coin2": "heads", "Coin3": "heads"}, 0.125)
        d.set_prob({"Coin1": "heads", "Coin2": "heads", "Coin3": "tails"}, 0.125)
        d.set_prob({"Coin1": "heads", "Coin2": "tails", "Coin3": "heads"}, 0.125)
        d.set_prob({"Coin1": "heads", "Coin2": "tails", "Coin3": "tails"}, 0.125)
        d.set_prob({"Coin1": "tails", "Coin2": "heads", "Coin3": "heads"}, 0.125)
        d.set_prob({"Coin1": "tails", "Coin2": "heads", "Coin3": "tails"}, 0.125)
        d.set_prob({"Coin1": "tails", "Coin2": "tails", "Coin3": "heads"}, 0.125)
        d.set_prob({"Coin1": "tails", "Coin2": "tails", "Coin3": "tails"}, 0.125)

        self.assertEqual(0.25, d.partial_prob({"Coin1": "heads", "Coin2": "tails"}))

    def test_partial_prob_not_here(self):
        d = Distribution({"Coin1": ["heads", "tails"], "Coin2": ["heads", "tails"], "Coin3": ["heads", "tails"]})

        self.assertRaises(IndexError, d.partial_prob, {"Rain": "true"})
