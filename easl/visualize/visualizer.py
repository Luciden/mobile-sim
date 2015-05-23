__author__ = 'Dennis'

import pygame


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


class Visualizer(object):
    # TODO: Add into actual simulation (real-time visualizing)
    # TODO: Implement visualizer interface in Entity and Controller
    # TODO: Make automatic layout-manager
    FG_COLOR = (255, 255, 255)
    BG_COLOR = (0, 0, 0)

    def __init__(self):
        pygame.init()

        self.size = 640, 640
        self.screen = pygame.display.set_mode(self.size)
        self.font = pygame.font.SysFont("monospace", 11)

        self.visualizations = {}

    def update_visualization(self, name, v):
        if v is None or name not in self.visualizations:
            return
        else:
            self.visualizations[name] = v

    def update_screen(self):
        """Draws all the current visualizations to the screen.
        """
        for name in self.visualizations:
            v = self.visualizations[name]
            if isinstance(v, Slider):
                self.__draw_slider(v)
            elif isinstance(v, Number):
                self.__draw_number(v)
            else:
                raise RuntimeError("Unknown type")

    def visualize_log(self, log):
        """
        Parameters
        ----------
        log : Log
            The data to visualize.
        """
        # Get the information from entities
        length = log.get_length()

        running = True
        time = 0
        while running and time < length:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            now = log.get_at_time(time)

            self.screen.fill((0, 0, 0))

            # Get all measurements
            for m in now:
                if m["_type"] == "measurement":
                    if m["entity"] == "infant":
                        # Draw the limb
                        self.screen.blit(self.__draw_limb("left-hand-position", m["left-hand-position"]), (16, 16))
                        self.screen.blit(self.__draw_limb("right-hand-position", m["right-hand-position"]), (128, 16))
                        self.screen.blit(self.__draw_limb("left-foot-position", m["left-foot-position"]), (16, 128))
                        self.screen.blit(self.__draw_limb("right-foot-position", m["right-foot-position"]), (128, 128))

            time += 1
            pygame.display.flip()
            pygame.time.delay(100)

    def __draw_limb(self, name, value):
        p = 0
        if value == "up":
            p = 0
        elif value == "middle":
            p = 1
        elif value == "down":
            p = 2

        return self.__draw_slider(Slider(name, 3, p))

    def __draw_visualization(self, visualization):
        if isinstance(visualization, Slider):
            return self.__draw_slider(visualization)
        elif isinstance(visualization, Number):
            return self.__draw_number(visualization)
        else:
            raise RuntimeError("Unknown type")

    def __draw_slider(self, slider):
        slider_width = 4
        block_width = 32
        length = slider.number * block_width

        block_y = (length / float(slider.number)) * slider.position

        # See how long the name is and adjust width accordingly
        name = self.font.render(slider.name, 1, Visualizer.FG_COLOR)
        width, name_height = name.get_size()

        if width < block_width:
            width = block_width

        surface = pygame.Surface((width, name_height + length))
        surface.fill(Visualizer.BG_COLOR)

        surface.blit(name, (0, 0))

        # Draw the slider base
        pygame.draw.rect(surface, Visualizer.FG_COLOR,
                         [width / 2 - slider_width / 2, name_height, slider_width, length])

        # Draw the slider block
        pygame.draw.rect(surface, Visualizer.FG_COLOR,
                         [width / 2 - block_width / 2, name_height + block_y, block_width, block_width])

        return surface

    def __draw_number(self, number):
        return self.font.render("{0}: {1}".format(number.name, number.number), 1, Visualizer.FG_COLOR)

    def __draw_grid(self, grid):
        # Make new grid of surfaces
        surface_grid = [[None for _ in range(grid.w)] for _ in range(grid.h)]

        # Find out which part is the biggest
        max_width = 0
        max_height = 0

        for x in range(grid.w):
            for y in range(grid.h):
                surface_grid[x][y] = self.__draw_visualization(grid[x][y])
                width, height = surface_grid[x][y].get_size()
                max_width = max(max_width, width)
                max_height = max(max_height, height)

        # Blit accordingly
        surface = pygame.Surface((grid.w * max_width, grid.h * max_height))
        surface.fill(Visualizer.BG_COLOR)
        for x in range(grid.w):
            for y in range(grid.h):
                surface.blit(surface_grid[x][y], (x * max_width, y * max_height))

        return surface
