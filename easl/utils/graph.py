__author__ = 'Dennis'


class NonExistentNodeError(Exception):
    pass


class NonExistentEdgeError(Exception):
    pass


class NodesNotUniqueError(Exception):
    pass


class Graph(object):
    # TODO: make more efficient by using dicts as internal representation.
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
    """
    def __init__(self):
        self.nodes = []
        self.edges = []

    def add_node(self, name):
        # Only have unique names, so check for existence
        if name not in self.nodes:
            self.nodes.append(name)

    def add_edge(self, a, b):
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
            self.edges.append((a, "", b, ""))
            self.edges.append((b, "", a, ""))

    def del_edge(self, a, b):
        self.__del_edge(a, b)
        self.__del_edge(b, a)

    def __del_edge(self, a, b):
        if a in self.nodes and b in self.nodes:
            for i in range(len(self.edges)):
                edge = self.edges[i]

                if edge[0] == a and edge[2] == b or edge[2] == a and edge[0] == b:
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
        pairs = self.get_pairs()

        return [(a, b, c)
                for (a, b) in pairs
                for (b, c) in pairs
                if a != c and a != b and b != c]

    def get_triples_special(self):
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

        # T   R
        for i in range(len(neighbours)):
            t, v, r = neighbours[i]
            if self.are_adjacent(t, r):
                del neighbours[i]

        return neighbours

    def orient(self, t, v, r):
        """
        For T - V - R, orients towards T -> V <- R

        Parameters
        ----------
        t : string
        v : string
        r : string
        """
        if t == v or t == r or v == r:
            raise NodesNotUniqueError("{0}, {1} and {2} are not unique nodes.".format(t, v, r))

        for i in range(len(self.edges)):
            (a, ma, b, mb) = self.edges[i]

            if (a == t and b == v) or (a == r and b == v):
                self.edges[i] = (a, "o", b, ">")
            elif (b == t and a == v) or (b == r and a == v):
                self.edges[i] = (a, ">", b, "o")
            else:
                raise LookupError("Edge not found.")

    def orient_half(self, x, y):
        """
        Orient X - Y as X -> Y
        """
        if not self.is_edge(x, y):
            raise NonExistentEdgeError("No edge between {0} and {1}".format(x, y))

        for i in range(len(self.edges)):
            (a, ma, b, mb) = self.edges[i]

            if a == x and b == y:
                self.edges[i] = (a, ma, b, ">")
            elif b == x and a == y:
                self.edges[i] = (a, ">", b, mb)
