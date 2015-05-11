from unittest import TestCase
from easl.agent import *

__author__ = 'Dennis'


class TestWorkingMemory(TestCase):
    def test_init(self):
        m = WorkingMemory()

        self.assertEqual(1, len(m.memory))

    def test_has_predicate(self):
        m = WorkingMemory()

        m.add_sensory(Predicate("Weather", "rain"))

        self.assertTrue(m.has_predicate(0, Predicate("Weather", "rain")))

    def test_age(self):
        m = WorkingMemory()

        m.add_sensory(Predicate("Weather", "rain"))

        m.age()

        self.assertTrue(m.has_predicate(1, Predicate("Weather", "rain")))

    def test_age_twice(self):
        m = WorkingMemory()

        m.add_sensory(Predicate("Weather", "rain"))

        m.age()
        m.age()

        self.assertTrue(m.has_predicate(2, Predicate("Weather", "rain")))

    def test_is_match(self):
        m = WorkingMemory()

        m.add_sensory(Predicate("Weather", "rain"))

        self.assertTrue(m.is_match([(Predicate("Weather", "rain"), WorkingMemory.NOW)]))

    def test_is_match_two(self):
        m = WorkingMemory()

        m.add_sensory(Predicate("Weather", "rain"))
        m.age()
        m.add_sensory(Predicate("Weather", "rain"))

        self.assertTrue(m.is_match([(Predicate("Weather", "rain"), WorkingMemory.NOW),
                                    (Predicate("Weather", "rain"), WorkingMemory.PREV)]))

    def test_is_match_no_match(self):
        m = WorkingMemory()

        m.add_sensory(Predicate("Weather", "rain"))
        m.age()

        self.assertFalse(m.is_match([(Predicate("Weather", "cloudy"), WorkingMemory.NOW)]))
