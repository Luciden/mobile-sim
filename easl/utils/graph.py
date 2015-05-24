__author__ = 'Dennis'

import math

import networkx as nx
import matplotlib.pyplot as plt


class NonExistentNodeError(Exception):
    pass


class NonExistentEdgeError(Exception):
    pass


class NodesNotUniqueError(Exception):
    pass


class Graph(object):
    """
    Representation of a graph that is used as a DAG representation for
    a Causal Bayes Net.

    Stores edges symmetrically (i.e. both a -> b and b -> a) for efficiency
    for the
    reasons.

    Attributes
    ----------
    nodes : [name]
    edges : [(name, tag, name, tag)]
    g : networkx.DiGraph
    """
    def __init__(self):
        self.nodes = []
        self.edges = []

        self.g = None

    def get_nodes(self):
        return self.nodes

    def get_edges(self):
        return self.edges

    def add_node(self, name):
        # Only have unique names, so check for existence
        if name not in self.nodes:
            self.nodes.append(name)

    def add_edge(self, a, b, ma="", mb=""):
        # Don't add edges reflexively to the same node
        if a == b:
            pass
        elif a not in self.nodes:
            raise NonExistentNodeError("{0} is not a node.".format(a))
        elif b not in self.nodes:
            raise NonExistentNodeError("{0} is not a node.".format(b))
        else:
            # Check if edge does not already exist
            for (x, mx, y, my) in self.edges:
                # When edge already exists, do nothing.
                if x == a and y == b:
                    return

            # Store edges symmetrically
            self.edges.append((a, ma, b, mb))
            self.edges.append((b, mb, a, ma))

    def del_edge(self, a, b):
        self.__del_edge(a, b)
        self.__del_edge(b, a)

    def __del_edge(self, a, b):
        if a in self.nodes and b in self.nodes:
            for i in range(len(self.edges)):
                (x, _, y, _) = self.edges[i]

                if x == a and y == b or y == a and x == b:
                    del self.edges[i]
                    return

    def empty(self):
        """
        Clear all nodes and edges to make an empty (null) graph.
        """
        self.nodes = []
        self.edges = []

    def is_node(self, name):
        return name in self.nodes

    def is_edge(self, a, b):
        return (a, b) in [(p, q) for (p, x, q, y) in self.edges]

    def make_complete(self, variables):
        """
        Parameters
        ----------
        variables : [string]
            Names of variables.
        """
        # Take only the nodes that are provided
        self.empty()
        self.nodes = variables

        n = len(self.nodes)

        if n <= 1:
            return

        for a in range(n - 1):
            for b in range(a+1, n):
                self.add_edge(self.nodes[a], self.nodes[b])

    def are_adjacent(self, a, b):
        """
        Parameters
        ----------
        a : string
            Variable name.
        b : string
            Variable name.
        """
        for e in self.edges:
            if e[0] == a and e[2] == b or e[0] == b and e[2] == a:
                return True
        return False

    def get_pairs(self):
        """
        All pairs A, B that are connected by an edge.

        Only contains edges in one direction, so if (A, B) is in pairs, (B, A)
        is not.

        Returns
        -------
        [(string, string)]
            pairs of variable names that are connected by an edge
        """
        pairs = []

        # Consider all pairs, but contains reversed pairs as well (a, b) and
        # (b, a)
        for (a, b) in [(a, b) for (a, _1, b, _2) in self.edges]:
            # Only add if
            if (b, a) in pairs:
                pass
            else:
                pairs.append((a, b))

        return pairs

    def get_directed_pairs(self):
        """
        All pairs A, B that are connected by an edge.

        Only contains edges in one direction, so if (A, B) is in pairs, (B, A)
        is not.

        Returns
        -------
        [(string, string)]
            pairs of variable names that are connected by an edge
        """
        pairs = []

        # Consider all pairs, but contains reversed pairs as well (a, b) and
        # (b, a)
        for (a, b) in [(a, b) for (a, _1, b, p) in self.edges if p == ">"]:
            # Only add if
            if (b, a) in pairs:
                pass
            else:
                pairs.append((a, b))

        return pairs

    def get_pairs_double(self):
        return [(a, b) for (a, _1, b, _2) in self.edges]

    def get_connected(self, a):
        """
        Finds all nodes that are connected by an edge to a specified node.

        Returns
        -------
        [string]
            Names of the nodes that it is connected to.
        """
        return [x for (b, _1, x, _2) in self.edges if b == a]

    def get_triples(self):
        """
        All triples of nodes A, B, C that are connected as A - B - C.

        Returns
        -------
        [(string, string, string)]
        """
        triples = []

        for (a, b, c) in self.get_triples_double():
            # Only add if
            if (c, b, a) in triples:
                pass
            else:
                triples.append((a, b, c))

        return triples

    def get_triples_double(self):
        pairs = self.get_pairs_double()

        return [(a, b, d)
                for (a, b) in pairs
                for (c, d) in pairs
                if a != d and a != d and b == c]

    def get_triples_special(self):
        """
        Get the triples T, V, R for which T has an edge with an arrowhead
        directed into V and V - R, and T has no edge connecting it to R.
        """
        triples = self.get_triples()
        # T ->V
        arrowheads = [(t, v, r)
                      for (t, v, r) in triples
                      for (t, _, v, a) in self.edges
                      if a == ">"]

        # V - R
        neighbours = [(t, v, r)
                      for (t, v, r) in arrowheads
                      for (v, _1, r, _2) in self.edges]

        # Remove those for which T and R are connected
        # T   R, 'T has no edge connecting it to R.'
        neighbours = [(t, v, r)
                      for (t, v, r) in neighbours
                      if not self.are_adjacent(t, r)]

        return neighbours

    def orient_half(self, x, y, m=None):
        """
        Orient X - Y as X -> Y
        """
        if not self.is_edge(x, y):
            raise NonExistentEdgeError("No edge between {0} and {1}".format(x, y))

        self.del_edge(x, y)
        self.add_edge(x, y, ma="o", mb=">")

    def visualize(self):

        pos = nx.spring_layout(self.g)

        nx.draw_networkx_nodes(self.g, pos)
        nx.draw_networkx_edges(self.g, pos)
        nx.draw_networkx_labels(self.g, pos)

        plt.savefig("graph.png")
        plt.show()

    def create_digraph(self):
        self.g = nx.DiGraph()

        for (a, l, b, r) in self.edges:
            if not self.g.has_edge(a, b) and r == ">":
                self.g.add_edge(a, b)

    def ancestors(self, x):
        return nx.ancestors(self.g, x)

    @staticmethod
    def arc_layout(n):
        """
        Creates a discrete, arced layout that does not have any edge intersect
        any nodes for a complete graph with the given number of nodes.

        Parameters
        ----------
        n : int
            Number of notes in the complete graph.

        Returns
        -------
        layout : [(int, int)]
            The (x, y) coordinates in the grid at which a node could be placed.
        """
        if n == 0:
            return []
        if n == 1:
            return [(0, 0)]
        if n == 2:
            return [(0, 1), (1, 0)]
        if n == 3:
            return [(0, 0), (2, 0), (0, 2)]
        else:
            half = Graph.half_layout(n - 1)
            half = Graph.shift_layout_down(half, 1)

            inverse = Graph.inverted_layout(half)

            return Graph.combine_layouts(half, inverse)

    @staticmethod
    def shift_layout_down(layout, n):
        if n == 0:
            return layout
        else:
            return Graph.shift_layout_down([(x, y + 1) for (x, y) in layout], n - 1)

    @staticmethod
    def half_layout(n):
        if n == 0:
            return []
        if n == 1:
            return [(0, 0)]
        if n == 2:
            return [(0, 1)]
        else:
            # Take a n/2 x n grid from the layout in n
            return [(x, y) for (x, y) in Graph.arc_layout(n)
                    if x <= (n / 2) - 1]

    @staticmethod
    def combine_layouts(a, b):
        # Check for double
        return list(set(a + b))

    @staticmethod
    def inverted_layout(layout):
        return [(y, x) for (x, y) in layout]

    @staticmethod
    def flipped_layout_horizontal(layout, n):
        return [(n - x - 1, y) for (x, y) in layout]

    @staticmethod
    def flipped_layout_vertical(layout, n):
        return [(x, n - y - 1) for (x, y) in layout]

    @staticmethod
    def flipped_layout_both(layout, n):
        return Graph.flipped_layout_horizontal(Graph.flipped_layout_vertical(layout, n), n)

    @staticmethod
    def layout_grid(layout):
        grid = [['.']]
        w = 1
        h = 1

        for (x, y) in layout:
            while x + 1 > w:
                grid[:] = [column + ['.'] for column in grid]
                w += 1
            while y + 1 > h:
                grid.append(['.' for _ in range(w)])
                h += 1

            grid[y][x] = 'O'

        return grid

    @staticmethod
    def print_layout(layout):
        ascii = ""
        for row in Graph.layout_grid(layout):
            ascii += ''.join(row) + '\n'

        return ascii
