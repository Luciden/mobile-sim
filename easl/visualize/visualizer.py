__author__ = 'Dennis'


class Visual(object):
    @staticmethod
    def visualize(self):
        """
        Parameters
        ----------
        self : object
            Any object that will be visualized.

        Returns
        -------
        visualization : Visualization
        """
        raise NotImplementedError("Base Class")


class Visualization(object):
    def __init__(self, name, show_name=False):
        self.name = name
        self.show_name = show_name


class Group(Visualization):
    def __init__(self, name):
        super(Group, self).__init__(name)

        self.elements = []

    def add_element(self, element):
        if element is not None:
            self.elements.append(element)

    def get_elements(self):
        return self.elements


class Rows(Group):
    def __init__(self, name):
        super(Rows, self).__init__(name)


class Columns(Group):
    def __init__(self, name):
        super(Columns, self).__init__(name)


class Slider(Visualization):
    """
    A slider with a fixed number of positions.

    A horizontal
    --|-----
    or vertical
    |
    +
    |
    slider.

    Attributes
    ----------
    name : string
    """
    def __init__(self, name, number, position):
        super(Slider, self).__init__(name)

        self.name = name
        self.number = number

        if 0 <= position < number:
            self.position = position
        else:
            raise RuntimeError("position not in slide")


class Table(Visualization):
    """
    A table.

        A    B
    C   1    0
    D   2    4

    Attributes
    ----------
    name : string
    """
    def __init__(self, name):
        super(Table, self).__init__(name)


class Tree(Visualization):
    def __init__(self, name, tree):
        """
        Attributes
        ----------
        tree : {name: {name: ...{name: value}}}
        """
        super(Tree, self).__init__(name)

        self.tree = tree


class Number(Visualization):
    def __init__(self, name, number):
        super(Number, self).__init__(name)

        self.number = number


class Grid(Visualization):
    def __init__(self, name, w, h):
        super(Grid, self).__init__(name)

        self.grid = [[None for _ in range(w)] for _ in range(h)]
        self.w = w
        self.h = h

    def add_element(self, element, y, x):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.grid[x][y] = element

    def element_at(self, x, y):
        return self.grid[x][y]


class List(Visualization):
    def __init__(self, name, elements):
        super(List, self).__init__(name)

        self.elements = elements


class Dict(Visualization):
    def __init__(self, name, elements):
        super(Dict, self).__init__(name)
        self.elements = elements


class Circle(Visualization):
    def __init__(self, name, v_min, v_max, v):
        super(Circle, self).__init__(name)

        self.v_min = v_min
        self.v_max = v_max
        self.v = v


class Graph(Visualization):
    def __init__(self, name, graph, nodes, edges, groups=None):
        super(Graph, self).__init__(name)
        self.graph = graph

        self.nodes = nodes
        self.edges = edges

        self.groups = groups


class Visualizer(object):
    def __init__(self):
        self.visualizations = None

    def reset_visualization(self):
        self.visualizations = Rows("main")

    def update_visualization(self, v):
        if v is None:
            return
        else:
            self.visualizations.add_element(v)

    def update(self, iteration):
        """Draws all the current visualizations to the screen.
        """
        raise NotImplementedError("Blah")
