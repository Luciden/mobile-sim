from unittest import TestCase
from easl.controller.new_causal_controller import *

__author__ = 'Dennis'


class TestDistributionComputer(TestCase):
    def test_compute_frequency_table(self):
        v = {"a_previous": ["x", "y"], "b_current": ["p", "q"]}

        d = Data()
        d.add_entry({"a": "x", "b": "p"})
        d.add_entry({"a": "x", "b": "p"})
        d.add_entry({"a": "x", "b": "p"})
        d.add_entry({"a": "x", "b": "q"})

        t, n = DistributionComputer.compute_frequency_table(v, d, ["a"])

        self.assertEqual(1, t.get_value({"a_previous": "x", "b_current": "p"}))
        self.assertEqual(1, t.get_value({"a_previous": "x", "b_current": "q"}))

    def test_compute_joint_probability_distribution(self):
        v = {"a_previous": ["x", "y"], "b_current": ["p", "q"]}

        d = Data()
        d.add_entry({"a": "x", "b": "p"})
        d.add_entry({"a": "x", "b": "p"})
        d.add_entry({"a": "x", "b": "p"})
        d.add_entry({"a": "x", "b": "q"})

        jpd = DistributionComputer.compute_joint_probability_distribution(v, d, ["a"])

        self.assertEqual(0.5, jpd.get_value({"a_previous": "x", "b_current": "p"}))
        self.assertEqual(0.5, jpd.get_value({"a_previous": "x", "b_current": "q"}))
        self.assertNotEqual(0.5, jpd.get_value({"a_previous": "y", "b_current": "p"}))
