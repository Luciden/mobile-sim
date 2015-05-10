from unittest import TestCase
from easl.agent.causal_agent import Data
from easl.utils import Distribution

__author__ = 'Dennis'


class TestData(TestCase):
    def test_add_entry(self):
        d = Data()

        d.add_entry({"move": "left"})

        self.assertIn({"move": "left"}, d.entries)

    def test_calculate_joint(self):
        d = Data()

        d.add_entry({"Coin1": "heads"})
        d.add_entry({"Coin1": "heads"})
        d.add_entry({"Coin1": "heads"})
        d.add_entry({"Coin1": "heads"})
        d.add_entry({"Coin1": "heads"})
        d.add_entry({"Coin1": "tails"})
        d.add_entry({"Coin1": "tails"})
        d.add_entry({"Coin1": "tails"})
        d.add_entry({"Coin1": "tails"})

        p = d.calculate_joint({"Coin1": ["heads", "tails"]})

        e = Distribution({"Coin1": ["heads", "tails"]})

        e.set_prob({"Coin1": "heads"}, 5/float(9))
        e.set_prob({"Coin1": "tails"}, 4/float(9))

        self.assertEqual(e, p)
