__author__ = 'Dennis'


class Graph(object):
    # TODO: make more efficient by using dicts as internal representation.
    """
    Attributes
    ----------
    nodes : [name]
    edges : (name, tag, name, tag)
    """
    def __init__(self):
        self.nodes = []
        self.edges = []

    def add_node(self, name):
        # Only have unique names, so check for existence
        if name not in self.nodes:
            self.nodes.append(name)

    def add_edge(self, a, b, ma="", mb=""):
        # Check if nodes actually exist
        if a in self.nodes and b in self.nodes:
            # Check if edge does not already exist
            for (x, mx, y, my) in self.edges:
                # When edge already exists, do nothing.
                if x == a and y == b:
                    return

            # Store edges symmetrically
            self.edges.append((a, ma, b, mb))
            self.edges.append((b, mb, a, ma))

    def del_edge(self, a, b):
        if a in self.nodes and b in self.nodes:
            for i in range(len(self.edges)):
                edge = self.edges[i]

                if edge[0] == a and edge[2] == b or edge[2] == a and edge[0] == b:
                    del self.edges[i]

    def empty(self):
        """
        Clear all nodes and edges to make an empty (null) graph.
        """
        self.nodes = []
        self.edges = []

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
        for e in self.edges:
            if e[0] == a and e[2] == b or e[0] == b and e[2] == a:
                return True
        return False

    def get_pairs(self):
        """

        Returns
        -------
        list
            pairs of variable names that are connected by an edge
        """
        return [(a, b) for (a, _, b, _) in self.edges]

    def get_connected(self, a):
        return [x for (b, x) in self.edges if b == a]

    def get_triples(self):
        return [(a, b, c) for (a, _, b, _) in self.edges for (b, _, c, _) in self.edges if a != c]

    def get_triples_special(self):
        triples = self.get_triples()
        # T ->V
        arrowheads = [(t, v, r) for (t, v, r) in triples for (t, _, v, a) in self.edges if a == ">"]

        # V - R
        neighbours = [(t, v, r) for (t, v, r) in arrowheads for (v, _, r, _) in self.edges]

        # T   R
        for i in range(len(neighbours)):
            t, v, r = neighbours[i]
            if self.are_adjacent(t, r):
                del neighbours[i]

        return neighbours

    def orient(self, t, v, r):
        for (a, ma, b, mb) in self.edges:
            if (a == t and b == v) or (a == r and b == v):
                ma = "o"
                mb = ">"
            elif (b == t and a == v) or (b == r and a == v):
                mb = "o"
                ma = ">"
            else:
                raise LookupError("Edge not found.")

    def orient_half(self, x, y):
        """
        Orient X - Y as X -> Y
        """
        for (a, ma, b, mb) in self.edges:
            if a == x and b == y:
                mb = ">"
            elif b == x and a == y:
                ma = ">"
            else:
                raise LookupError("Edge not found.")
