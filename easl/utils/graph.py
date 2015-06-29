__author__ = 'Dennis'

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
        self.g = nx.DiGraph()

    def get_nodes(self):
        return nx.nodes(self.g)

    def get_edges(self):
        return nx.edges(self.g)

    def add_node(self, name):
        # Only have unique names, so check for existence
        self.g.add_node(name)

    def add_edge(self, a, b, causal=False):
        """
        Add an undirected edge, i.e. both ways.
        """
        # Don't add edges reflexively to the same node
        if a == b:
            pass
        elif not self.g.has_node(a):
            raise NonExistentNodeError("{0} is not a node.".format(a))
        elif not self.g.has_node(b):
            raise NonExistentNodeError("{0} is not a node.".format(b))
        else:
            self.g.add_edge(a, b)
            if causal:
                self.g[a][b]["from"] = ""
                self.g[a][b]["to"] = ">"
            else:
                self.g.add_edge(b, a)

    def del_edge(self, a, b):
        if self.g.has_edge(a, b):
            self.g.remove_edge(a, b)
        if self.g.has_edge(b, a):
            self.g.remove_edge(b, a)

    def empty(self):
        """
        Clear all nodes and edges to make an empty (null) graph.
        """
        self.g.clear()

    def has_node(self, name):
        return self.g.has_node(name)

    def has_edge(self, a, b):
        return self.g.has_edge(a, b)

    def make_complete(self, variables):
        """
        Parameters
        ----------
        variables : [string]
            Names of variables.
        """
        # Take only the nodes that are provided
        self.empty()
        self.g.add_nodes_from(variables)

        n = len(variables)

        for a in range(n - 1):
            for b in range(a+1, n):
                self.add_edge(variables[a], variables[b])

    def are_adjacent(self, a, b):
        """
        Parameters
        ----------
        a : string
            Variable name.
        b : string
            Variable name.
        """
        return self.g.has_edge(a, b) or self.g.has_edge(b, a)

    def get_connected(self, a):
        """
        Finds all nodes that are connected by an edge to a specified node.

        Returns
        -------
        [string]
            Names of the nodes that it is connected to.
        """
        return set(nx.all_neighbors(self.g, a))

    def arrow_from(self, a):
        """
        All nodes that have an arrow directed into them from the current node.
        """
        arrows = []
        for b in nx.all_neighbors(self.g, a):
            if self.g.has_edge(a, b) and "to" in self.g[a][b] and self.g[a][b] == ">":
                arrows.append(b)

        return arrows

    def orient_half(self, x, y):
        """
        Orient X - Y as X o-> Y
        """
        if not self.has_edge(x, y):
            raise NonExistentEdgeError("No edge between {0} and {1}".format(x, y))

        # Stored edges in both directions until now, so remove the reverse one
        if self.has_edge(y, x):
            self.g.remove_edge(y, x)

        # Mark the edge
        self.g[x][y]["from"] = "o"
        self.g[x][y]["to"] = ">"

    def visualize(self):
        pos = nx.spring_layout(self.g)

        nx.draw_networkx_nodes(self.g, pos)
        nx.draw_networkx_edges(self.g, pos)
        nx.draw_networkx_labels(self.g, pos)

        plt.savefig("graph.png")
        plt.show()

    def ancestors(self, x):
        return nx.ancestors(self.g, x)

    def is_dag(self):
        return nx.is_directed_acyclic_graph(self.g)

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
        if n % 2 == 0:
            half = Graph.half_layout(n - 1)
            half = Graph.shift_layout_down(half, 1)

            inverse = Graph.inverted_layout(half)

            return Graph.combine_layouts(half, inverse)
        else:
            half = Graph.half_layout(n - 1)
            half = Graph.shift_layout_down(half, n / 2)

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
