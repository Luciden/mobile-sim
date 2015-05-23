__author__ = 'Dennis'

from visualizer import *

import pygame


class PyGameVisualizer(Visualizer):
    FG_COLOR = (255, 255, 255)
    BG_COLOR = (0, 0, 0)

    def __init__(self):
        super(PyGameVisualizer, self).__init__()

        pygame.init()

        self.size = 640, 640
        self.screen = pygame.display.set_mode(self.size)
        self.font = pygame.font.SysFont("monospace", 11)

    def update(self):
        """Draws all the current visualizations to the screen.
        """
        # Close the window if it is closed
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # TODO: Make the visualization stop somehow
                    running = False

        self.screen.fill(PyGameVisualizer.BG_COLOR)
        self.screen.blit(self.__draw_visualization(self.visualizations), (0, 0))

        pygame.display.flip()
        pygame.time.delay(100)

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
            grid = Grid("infant", 2, 2)
            for m in now:
                if m["_type"] == "measurement":
                    if m["entity"] == "infant":
                        positions = {"up": 0, "middle": 1, "down": 2}

                        grid.add_element(Slider("left-hand-position", 3, positions[m["left-hand-position"]]), 0, 0)
                        grid.add_element(Slider("right-hand-position", 3, positions[m["right-hand-position"]]), 0, 1)
                        grid.add_element(Slider("left-foot-position", 3, positions[m["left-foot-position"]]), 1, 0)
                        grid.add_element(Slider("right-foot-position", 3, positions[m["right-foot-position"]]), 1, 1)

            self.screen.blit(self.__draw_grid(grid), (0, 0))

            time += 1
            pygame.display.flip()
            pygame.time.delay(100)

    def __draw_visualization(self, v):
        if isinstance(v, Slider):
            return self.__draw_slider(v)
        elif isinstance(v, Number):
            return self.__draw_number(v)
        elif isinstance(v, Grid):
            return self.__draw_grid(v)
        elif isinstance(v, Tree):
            return self.__draw_tree(v)
        elif isinstance(v, Group):
            return self.__draw_group(v)
        else:
            raise RuntimeError("Unknown type")

    def __draw_slider(self, slider):
        slider_width = 4
        block_width = 32
        length = slider.number * block_width

        block_y = (length / float(slider.number)) * slider.position

        # See how long the name is and adjust width accordingly
        name = self.font.render(slider.name, 1, PyGameVisualizer.FG_COLOR)
        width, name_height = name.get_size()

        if width < block_width:
            width = block_width

        surface = pygame.Surface((width, name_height + length))
        surface.fill(PyGameVisualizer.BG_COLOR)

        surface.blit(name, (0, 0))

        # Draw the slider base
        pygame.draw.rect(surface, PyGameVisualizer.FG_COLOR,
                         [width / 2 - slider_width / 2, name_height, slider_width, length])

        # Draw the slider block
        pygame.draw.rect(surface, PyGameVisualizer.FG_COLOR,
                         [width / 2 - block_width / 2, name_height + block_y, block_width, block_width])

        return surface

    def __draw_number(self, number):
        return self.font.render("{0}: {1}".format(number.name, number.number), 1, PyGameVisualizer.FG_COLOR)

    def __draw_grid(self, grid):
        # Make new grid of surfaces
        surface_grid = [[None for _ in range(grid.w)] for _ in range(grid.h)]

        # Find out which part is the biggest
        max_width = 0
        max_height = 0

        for x in range(grid.w):
            for y in range(grid.h):
                surface_grid[x][y] = self.__draw_visualization(grid.element_at(x, y))
                width, height = surface_grid[x][y].get_size()
                max_width = max(max_width, width)
                max_height = max(max_height, height)

        # Blit accordingly
        surface = pygame.Surface((grid.w * max_width, grid.h * max_height))
        surface.fill(PyGameVisualizer.BG_COLOR)
        for x in range(grid.w):
            for y in range(grid.h):
                surface.blit(surface_grid[x][y], (x * max_width, y * max_height))

        return surface

    def __draw_tree(self, tree, indent=0):
        if isinstance(tree, Tree):
            return self.__draw_tree(tree.tree)
        # Main case: for all branches, make the indented rest
        elif isinstance(tree, dict):
            # Make all branches
            branches = []
            for name in tree:
                branches.append(self.font.render(indent * "  " + name, 1, PyGameVisualizer.FG_COLOR))
                branches.append(self.__draw_tree(tree[name], indent + 1))

            # Find largest one and prepare surface
            max_width = 0
            total_height = 0
            for branch in branches:
                width, height = branch.get_size()
                max_width = max(max_width, width)
                total_height += height

            # Draw all branches to the surface and return
            surface = pygame.Surface((max_width, total_height))
            surface.fill(PyGameVisualizer.BG_COLOR)

            y = 0
            for branch in branches:
                _, height = branch.get_size()

                surface.blit(branch, (0, y))

                y += height

            return surface
        # Base case: just print the value
        else:
            return self.font.render(indent * "  " + str(tree), 1, PyGameVisualizer.FG_COLOR)

    def __draw_group(self, group):
        # Draw every element, take its size and draw the next after it
        elements = []
        x = 0
        max_y = 0

        # Find the dimensions of the surface
        for element in group.get_elements():
            e = self.__draw_visualization(element)
            elements.append(e)
            w, h = e.get_size()

            x += w
            max_y = max(max_y, h)

        # Blit to surface
        surface = pygame.Surface((x, max_y))
        surface.fill(PyGameVisualizer.BG_COLOR)

        x = 0
        for e in elements:
            w, h = e.get_size()
            surface.blit(e, (x, 0))

            x += w

        return surface
