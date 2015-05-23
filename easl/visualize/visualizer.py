__author__ = 'Dennis'


class Visualization(object):
    pass


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

    def add_element(self, element, x, y):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.grid[x][y] = element

    def element_at(self, x, y):
        return self.grid[x][y]


class Visualizer(object):
    def __init__(self):
        self.visualizations = {}

    def update_visualization(self, name, v):
        if v is None or name not in self.visualizations:
            return
        else:
            self.visualizations[name] = v

    def update(self):
        """Draws all the current visualizations to the screen.
        """
        raise NotImplementedError("Blah")
