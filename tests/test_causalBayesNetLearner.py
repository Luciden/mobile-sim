from unittest import TestCase
from easl import utils
from easl.agent import CausalBayesNetLearner
from easl.agent import Data

__author__ = 'Dennis'


class TestCausalBayesNetLearner(TestCase):
    def setUp(self):
        # Room world
        #
        # open -> door <- close
        #     \          /
        #      > window <
        self.room_actions = {"Open": ["door", "window", "none"], "Close": ["door", "window", "none"]}
        self.room_sensories = {"Door": ["open", "closed"], "Window": ["open", "closed"]}
        self.room_variables = self.room_actions
        self.room_variables.update(self.room_sensories)

        self.room_complete = utils.Graph()
        self.room_complete.make_complete(self.room_variables.keys())

        # Coin world
        #
        # Coin1    Coin2
        #
        self.coin_actions = {}
        self.coin_sensories = {"Coin1": ["heads", "tails"], "Coin2": ["heads", "tails"]}
        self.coin_variables = {}
        self.coin_variables.update(self.coin_sensories)

        self.coin_complete = utils.Graph()
        self.coin_complete.make_complete(self.coin_variables.keys())

        #
        #
        # Work  \
        #         Sleepy
        # Drink /
        self.sleep_actions = {}
        self.sleep_sensories = {"Sleepy": ["yes", "no"], "Work": ["yes", "no"], "Drink": ["yes", "no"]}
        self.sleep_variables = {}
        self.sleep_variables.update(self.sleep_actions)
        self.sleep_variables.update(self.sleep_sensories)

        self.sleep_complete = utils.Graph()
        self.sleep_complete.make_complete(self.sleep_variables.keys())

    def test_step_2_coin(self):
        d = Data()
        d.add_entry({"Coin1": "tails", "Coin2": "heads"}, 0)
        d.add_entry({"Coin1": "tails", "Coin2": "heads"}, 1)
        d.add_entry({"Coin1": "tails", "Coin2": "heads"}, 2)
        d.add_entry({"Coin1": "tails", "Coin2": "heads"}, 3)
        d.add_entry({"Coin1": "tails", "Coin2": "heads"}, 4)

        CausalBayesNetLearner.step_2(self.coin_actions, self.coin_sensories, self.coin_complete, d)

        self.assertEqual(0, len(self.coin_complete.edges))

    def test_step_2(self):
        d = Data()
        d.add_entry({"Door": "closed", "Window": "closed", "Open": "door", "Close": "none"}, 0)
        d.add_entry({"Door": "open", "Window": "closed", "Open": "none", "Close": "none"}, 1)
        d.add_entry({"Door": "open", "Window": "closed", "Open": "window", "Close": "none"}, 2)
        d.add_entry({"Door": "open", "Window": "open", "Open": "none", "Close": "none"}, 3)

        CausalBayesNetLearner.step_2(self.room_actions, self.room_sensories, self.room_complete, d)

        self.assertIn(("Door", "", "Open", ""), self.room_complete.edges)
        self.assertIn(("Window", "", "Open", ""), self.room_complete.edges)

    def test_step_3(self):
        d = Data()
        d.add_entry({"Drink": "no", "Work": "no", "Sleepy": "no"}, 0)
        d.add_entry({"Drink": "yes", "Work": "no", "Sleepy": "yes"}, 1)
        d.add_entry({"Drink": "yes", "Work": "yes", "Sleepy": "yes"}, 2)
        d.add_entry({"Drink": "no", "Work": "yes", "Sleepy": "yes"}, 2)

        CausalBayesNetLearner.step_3(self.sleep_actions, self.sleep_sensories, self.sleep_complete, [], d)

        self.assertIn(("Drink", "", "Sleepy", ""), self.sleep_complete.edges)
        self.assertIn(("Work", "", "Sleepy", ""), self.sleep_complete.edges)
        self.assertNotIn(("Drink", "", "Work", ""), self.sleep_complete.edges)
