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
    pass


class Group(Visualization):
    def __init__(self, name):
        self.name = name

        self.elements = []

    def add_element(self, element):
        self.elements.append(element)

    def get_elements(self):
        return self.elements


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
    def __init__(self):
        pass


class Tree(Visualization):
    def __init__(self, name, tree):
        """
        Attributes
        ----------
        tree : {name: {name: ...{name: value}}}
        """
        self.name = name
        self.tree = tree


class Number(Visualization):
    def __init__(self, name, number):
        self.name = name
        self.number = number


class Grid(Visualization):
    def __init__(self, name, w, h):
        self.name = name
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
        self.name = name
        self.elements = elements


class Visualizer(object):
    def __init__(self):
        self.visualizations = None

    def reset_visualization(self):
        self.visualizations = Group("main")

    def update_visualization(self, v):
        if v is None:
            return
        else:
            self.visualizations.add_element(v)

    def update(self):
        """Draws all the current visualizations to the screen.
        """
        raise NotImplementedError("Blah")
