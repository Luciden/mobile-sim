from unittest import TestCase

from easl.mechanisms.operant_controller import *

__author__ = 'Dennis'


class TestReinforcer(TestCase):
    def test_increment_conjunctions(self):
        m = WorkingMemory()

        m.add_action(Predicate("Open", "door"))
        m.add_sensory(Predicate("Door", "closed"))
        m.age()
        m.add_sensory(Predicate("Door", "open"))

        r = Reinforcer(Predicate("Door", "open"))

        r.increment_conjunctions(m)
