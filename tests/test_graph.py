from unittest import TestCase
from easl.utils import Graph

__author__ = 'Dennis'


class TestGraph(TestCase):
    def test_add_node_from_empty(self):
        g = Graph()

        g.add_node("a")
        self.assertIn("a", g.nodes)

    def test_add_node_extra(self):
        g = Graph()

        g.add_node("a")
        g.add_node("b")

        self.assertIn("a", g.nodes)
        self.assertIn("b", g.nodes)
