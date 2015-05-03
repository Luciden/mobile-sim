__author__ = 'Dennis'


class Graph(object):
    # TODO(Dennis): Make more efficient. (Store edges symmetrically?)
    """
    """
    def __init__(self):
        self.nodes = []
        self.edges = []

    def add_node(self, name):
        # Only have unique names, so check for existence
        if name not in self.nodes:
            self.nodes.append(name)

    def add_edge(self, a, b, ma="", mb=""):
        if a in self.nodes and b in self.nodes:
            self.edges.append((a, ma, b, mb))

    def del_edge(self, a, b):
        if a in self.nodes and b in self.nodes:
            for i in range(len(self.edges)):
                edge = self.edges[i]

                if edge[0] == a and edge[2] == b:
                    del self.edges[i]

    def empty(self):
        """
        Clear all nodes and edges
        """
        self.nodes = []
        self.edges = []

    def make_complete(self, variables):
        # Take only the nodes that are provided
        self.empty()
        self.nodes = variables

        for a in range(len(self.nodes)):
            for b in range(a+1, len(self.nodes)):
                edge = (self.nodes[a], "", self.nodes[b], "")
                self.edges.append(edge)

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

    def get_triples(self):
        triples = [(a, b, c) for (a, _, b, _) in self.edges for (b, _, c, _) in self.edges if a != c]
        # also check edges that are stored in reverse
        triples += [(a, b, c) for (b, _, a, _) in self.edges for (b, _, c, _) in self.edges if a != c]

        return triples

    def get_triples_special(self):
        triples = self.get_triples()
        # T ->V
        arrowheads = [(t, v, r) for (t, v, r) in triples for (t, _, v, ">") in self.edges]
        arrowheads += [(t, v, r) for (t, v, r) in triples for (v, ">", t, _) in self.edges]

        # V - R
        neighbours = [(t, v, r) for (t, v, r) in arrowheads for (v, _, r, _) in self.edges]
        neighbours += [(t, v, r) for (t, v, r) in arrowheads for (r, _, r, ) in self.edges]
        # T   R
        for i in range(len(neighbours)):
            t, v, r = neighbours[i]
            if self.are_adjacent(t, r):
                del neighbours[i]

        return neighbours

    def orient(self, t, v, r):
        # TODO(Dennis): error checking for existence
        for (a, ma, b, mb) in self.edges:
            if (a == t and b == v) or (a == r and b == v):
                ma = "o"
                mb = ">"
            elif (b == t and a == v) or (b == r and a == v):
                mb = "o"
                ma = ">"
            else:
                # error not found
                pass

    def orient_half(self, x, y):
        """
        Orient X - Y as X -> Y
        """
        for (a, ma, b, mb) in self.edges:
            if (a == x and b == y):
                mb = ">"
            elif (b == x and a == y):
                ma = ">"
            else:
                # error not found
                pass
