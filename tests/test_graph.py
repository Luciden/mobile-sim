from unittest import TestCase
from easl.utils import *

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

    def test_add_node_add_double(self):
        g = Graph()

        g.add_node("a")
        g.add_node("a")

        self.assertIn("a", g.nodes)
        self.assertEqual(1, len(g.nodes))

    def test_add_edge_reflexive(self):
        g = Graph()

        g.add_node("a")

        g.add_edge("a", "a")

        # No edge should have been added
        self.assertEqual(0, len(g.edges))

    def test_add_edge_normal(self):
        g = Graph()

        g.add_node("a")
        g.add_node("b")

        g.add_edge("a", "b")

        self.assertIn(("a", "", "b", ""), g.edges)
        self.assertIn(("b", "", "a", ""), g.edges)

    def test_add_edge_nonexistent_node(self):
        g = Graph()

        g.add_node("a")

        self.assertRaises(NonExistentNodeError, g.add_edge, "a", "b")

    def test_del_edge_normal(self):
        g = Graph()

        g.add_node("a")
        g.add_node("b")

        g.add_edge("a", "b")

        g.del_edge("a", "b")

        self.assertEqual(0, len(g.edges))

    def test_empty(self):
        g = Graph()

        g.add_node("a")
        g.add_node("b")

        g.add_edge("a", "b")

        g.empty()

        self.assertEqual(0, len(g.nodes))
        self.assertEqual(0, len(g.edges))

    def test_is_node_normal(self):
        g = Graph()

        g.add_node("a")

        self.assertTrue(g.is_node("a"))

    def test_is_node_none(self):
        g = Graph()

        self.assertFalse(g.is_node("a"))

    def test_is_edge_normal(self):
        g = Graph()

        g.add_node("a")
        g.add_node("b")

        g.add_edge("a", "b")

        self.assertTrue(g.is_edge("a", "b"))
        self.assertTrue(g.is_edge("b", "a"))

    def test_make_complete_empty(self):
        g = Graph()

        g.make_complete([])

        self.assertEqual(0, len(g.nodes))
        self.assertEqual(0, len(g.edges))

    def test_make_complete_single(self):
        g = Graph()

        g.make_complete(["a"])

        self.assertTrue(g.is_node("a"))
        self.assertEqual(0, len(g.edges))

    def test_make_complete_multiple(self):
        g = Graph()

        g.make_complete(["a", "b", "c"])

        self.assertTrue(g.is_node("a"))
        self.assertTrue(g.is_node("b"))
        self.assertTrue(g.is_node("c"))

        self.assertTrue(g.is_edge("a", "b"))
        self.assertTrue(g.is_edge("a", "c"))
        self.assertTrue(g.is_edge("b", "c"))

    def test_are_adjacent_adjacent(self):
        g = Graph()

        g.add_node("a")
        g.add_node("b")

        g.add_edge("a", "b")

        self.assertTrue(g.are_adjacent("a", "b"))

    def test_are_adjacent_not_adjacent(self):
        g = Graph()

        g.add_node("a")
        g.add_node("b")

        self.assertFalse(g.are_adjacent("a", "b"))

    def test_get_pairs_empty(self):
        g = Graph()

        self.assertEqual([], g.get_pairs())

    def test_get_pairs_single(self):
        g = Graph()

        g.add_node("a")

        self.assertEqual([], g.get_pairs())

    def test_get_pairs_multiple(self):
        g = Graph()

        g.add_node("a")
        g.add_node("b")
        g.add_node("c")

        g.add_edge("a", "b")

        pairs = g.get_pairs()

        self.assertEqual(1, len(pairs))
        self.assertTrue(("a", "b") in pairs or ("b", "a") in pairs)

    def test_get_pairs_none(self):
        g = Graph()

        g.add_node("a")
        g.add_node("b")

        self.assertEqual([], g.get_connected("a"))

    def test_get_connected_multiple(self):
        g = Graph()

        g.make_complete(["a", "b", "c"])

        self.assertItemsEqual(["b", "c"], g.get_connected("a"))

    def test_get_triples(self):
        g = Graph()

        g.add_node("a")
        g.add_node("b")
        g.add_node("c")
        g.add_node("d")
        g.add_node("e")

        g.add_edge("a", "b")
        g.add_edge("b", "c")
        g.add_edge("a", "d")

        triples = g.get_triples()

        self.assertEqual(2, len(triples))
        self.assertTrue(("a", "b", "c") in triples or ("c", "b", "a") in triples)
        self.assertTrue(("b", "a", "d") in triples or ("d", "a", "b") in triples)

    def test_orient_half_normal(self):
        g = Graph()

        g.add_node("a")
        g.add_node("b")

        g.add_edge("a", "b")

        g.orient_half("a", "b")

        self.assertTrue(("a", "", "b", ">") in g.edges)
        self.assertTrue(("b", ">", "a", "") in g.edges)

    def test_orient_half_not_existent(self):
        g = Graph()

        g.add_node("a")
        g.add_node("b")

        self.assertRaises(NonExistentEdgeError, g.orient_half, "a", "b")

    def test_get_triples_special_single(self):
        g = Graph()

        g.add_node("t")
        g.add_node("v")
        g.add_node("r")

        g.add_edge("t", "v")
        g.orient_half("t", "v")

        g.add_edge("v", "r")

        triples = g.get_triples_special()

        self.assertTrue(("t", "v", "r") in triples)

    def test_get_triples_special_empty(self):
        g = Graph()

        triples = g.get_triples_special()

        self.assertEqual([], triples)

    def test_causal_paths_single_path(self):
        g = Graph()

        g.add_node("a")
        g.add_node("b")
        g.add_node("c")

        g.add_edge("a", "b")

        g.orient_half("a", "b")

        paths = g.causal_paths("b")

        self.assertEqual(1, len(paths))
        self.assertIn(["a", "b"], paths)

    def test_causal_paths_no_path(self):
        g = Graph()

        g.add_node("a")
        g.add_node("b")
        g.add_node("c")

        g.add_edge("a", "b")

        paths = g.causal_paths("b")

        self.assertEqual(0, len(paths))
