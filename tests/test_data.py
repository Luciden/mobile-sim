from unittest import TestCase
from easl.controller.causal_controller import Data
from easl.utils import Distribution

__author__ = 'Dennis'


class TestData(TestCase):
    def test_add_entry(self):
        d = Data()

        d.add_entry({"move": "left"}, 0)

        self.assertTrue("move" in d.entries[0])
        self.assertTrue(d.entries[0]["move"] == "left")

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

        p = d.calculate_joint_flat({"Coin1": ["heads", "tails"]})

        e = Distribution({"Coin1": ["heads", "tails"]})

        e.set_prob({"Coin1": "heads"}, 5/float(9))
        e.set_prob({"Coin1": "tails"}, 4/float(9))

        self.assertEqual(e, p)

    def test_calculate_joint_multiple(self):
        d = Data()

        d.add_entry({"Weather": "clear", "Temperature": "warm"})
        d.add_entry({"Weather": "clear", "Temperature": "warm"})
        d.add_entry({"Weather": "clear", "Temperature": "warm"})
        d.add_entry({"Weather": "clear", "Temperature": "warm"})
        d.add_entry({"Weather": "clear", "Temperature": "cold"})
        d.add_entry({"Weather": "clear", "Temperature": "cold"})
        d.add_entry({"Weather": "cloudy", "Temperature": "warm"})
        d.add_entry({"Weather": "cloudy", "Temperature": "cold"})
        d.add_entry({"Weather": "cloudy", "Temperature": "cold"})
        d.add_entry({"Weather": "cloudy", "Temperature": "cold"})

        p = d.calculate_joint_flat({"Weather": ["clear", "cloudy"], "Temperature": ["warm", "cold"]})

        e = Distribution({"Weather": ["clear", "cloudy"], "Temperature": ["warm", "cold"]})

        e.set_prob({"Weather": "clear", "Temperature": "warm"}, 0.4)
        e.set_prob({"Weather": "clear", "Temperature": "cold"}, 0.2)
        e.set_prob({"Weather": "cloudy", "Temperature": "warm"}, 0.1)
        e.set_prob({"Weather": "cloudy", "Temperature": "cold"}, 0.3)

        self.assertEqual(e, p)

    def test_calculate_join_with_time(self):
        d = Data()

        d.add_entry({"Open": "none", "Door": "closed"}, 0)
        d.add_entry({"Open": "door", "Door": "closed"}, 1)
        d.add_entry({"Open": "none", "Door": "open"}, 2)
        d.add_entry({"Open": "door", "Door": "open"}, 3)
        d.add_entry({"Open": "none", "Door": "open"}, 4)

        p = d.calculate_joint({"Open": ["door", "none"]}, {"Door": ["open", "closed"]})

        e = Distribution({"Open_prev": ["door", "none"],
                          "Door_prev": ["open", "closed"],
                          "Door": ["open", "closed"]})

        e.set_prob({"Open_prev": "none", "Door_prev": "closed", "Door": "closed"}, 1/float(4))
        e.set_prob({"Open_prev": "door", "Door_prev": "closed", "Door": "open"}, 1/float(4))
        e.set_prob({"Open_prev": "none", "Door_prev": "open", "Door": "open"}, 1/float(4))
        e.set_prob({"Open_prev": "door", "Door_prev": "open", "Door": "open"}, 1/float(4))

        print e.table
        print p.table

        self.assertTrue(e == p)
