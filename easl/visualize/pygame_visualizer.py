__author__ = 'Dennis'

from visualizer import *
import easl

import sys
import pygame
import math


class PyGameVisualizer(Visualizer):
    BG_COLOR = (0, 0, 0)
    FG_COLOR = (255, 255, 255)
    OBJ_COLOR = (196, 0, 0)

    def __init__(self):
        super(PyGameVisualizer, self).__init__()

        pygame.init()

        self.world = None

        self.size = 1600, 900
        self.screen = pygame.display.set_mode(self.size)
        self.font = pygame.font.SysFont("monospace", 11)

        self.step = False
        self.paused = False

        self.parameters = {"dt": 100}

        self.keys = ["space: pause/unpause the simulation",
                     "s: step once and pause"]

    def set_world(self, world):
        self.world = world

    def reset_visualization(self):
        super(PyGameVisualizer, self).reset_visualization()

        # Add a keymap
        self.visualizations.add_element(List("Key Bindings", self.keys))
        # Add the currently set parameters
        self.visualizations.add_element(Dict("Parameters", self.parameters))

    def update(self):
        """Draws all the current visualizations to the screen.
        """
        self.screen.fill(PyGameVisualizer.BG_COLOR)
        self.screen.blit(self.__draw_visualization(self.visualizations), (0, 0))

        pygame.display.flip()
        pygame.time.delay(self.parameters["dt"])

        if self.step:
            self.step = False
            self.__pause()
        else:
            self.__handle_keys()
            if self.paused:
                self.__pause()

    def __handle_keys(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.paused:
                        self.paused = False
                        self.step = False
                    else:
                        self.paused = True
                        self.step = False
                if event.key == pygame.K_s:
                    self.step = True
                    self.paused = True
                if event.key == pygame.K_UP:
                    self.parameters["dt"] += 100
                if event.key == pygame.K_DOWN:
                    self.parameters["dt"] -= 100
                if event.key == pygame.K_EQUALS:
                    self.world.add_trigger("infant", "right-foot-position", "movement", "mobile")
                if event.key == pygame.K_MINUS:
                    self.world.remove_trigger("infant", "right-foot-position", "movement", "mobile")

    def __pause(self):
        # TODO: Redraw screen while paused.
        while self.paused and not self.step:
            self.__handle_keys()

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
            pygame.time.delay(self.parameters["dt"])

    def __draw_visualization(self, v):
        if isinstance(v, Slider):
            return self.__draw_slider(v)
        elif isinstance(v, Number):
            return self.__draw_number(v)
        elif isinstance(v, Grid):
            return self.__draw_grid(v)
        elif isinstance(v, Tree):
            return self.__draw_tree(v)
        elif isinstance(v, Rows):
            return self.__draw_rows(v)
        elif isinstance(v, Group):
            return self.__draw_group(v)
        elif isinstance(v, List):
            return self.__draw_list(v)
        elif isinstance(v, Dict):
            return self.__draw_dict(v)
        elif isinstance(v, Circle):
            return self.__draw_circle(v)
        elif isinstance(v, Graph):
            return self.__draw_graph(v)
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

        margin = pygame.Surface((8, 1))

        # Find the dimensions of the surface
        for element in group.get_elements():
            elements.append(margin)
            x += margin.get_width()

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

    def __draw_list(self, lst):
        max_width = 0
        total_height = 0

        elements = []

        for element in lst.elements:
            e = self.font.render(str(element), 1, self.FG_COLOR)

            max_width = max(max_width, e.get_width())
            total_height += e.get_height()

            elements.append(e)

        surface = pygame.Surface((max_width, total_height))
        surface.fill(PyGameVisualizer.BG_COLOR)

        y = 0
        for e in elements:
            surface.blit(e, (0, y))

            y += e.get_height()

        return surface

    def __draw_dict(self, dct):
        max_width = 0
        total_height = 0

        elements = []

        for element in dct.elements:
            e = self.font.render("%s: %s" % (str(element), str(dct.elements[element])), 1, self.FG_COLOR)

            max_width = max(max_width, e.get_width())
            total_height += e.get_height()

            elements.append(e)

        surface = pygame.Surface((max_width, total_height))
        surface.fill(PyGameVisualizer.BG_COLOR)

        y = 0
        for e in elements:
            surface.blit(e, (0, y))

            y += e.get_height()

        return surface

    def __draw_circle(self, circle):
        delta_v = 8
        d_max = 2 * circle.v_max * delta_v
        center_x = center_y = d_max / 2

        radius = delta_v * circle.v

        surface = pygame.Surface((d_max, d_max))
        surface.fill(self.BG_COLOR)

        pygame.draw.circle(surface, self.FG_COLOR, (center_x, center_y), radius)

        return surface

    def __draw_graph(self, graph):
        node_radius = 16
        spacing = 6 * node_radius  # Distance between adjacent nodes' centers
        coordinates = {}

        # If no groups were given, do a column layout
        if graph.groups is None:
            max_columns = 3
            width = 2 * node_radius * max_columns + (max_columns - 1) * spacing

            # Distribute node positions and store coordinates
            x = node_radius
            y = node_radius
            for node in graph.nodes:
                coordinates[node] = (x, y)
                x += spacing

                if x > width - node_radius:
                    x = node_radius
                    y += spacing

            height = y + node_radius
        # If groups were given, do arc layouts
        else:
            left_width = 0
            top_height = 0
            right_width = 0
            bottom_height = 0

            layout = None
            n_group = 0
            for group in graph.groups:
                n = len(group)
                if n_group == 0:
                    layout = easl.utils.Graph.arc_layout(n)
                    left_width = top_height = n * 2 * node_radius + (n - 1) * spacing
                elif n_group == 1:
                    layout = easl.utils.Graph.flipped_layout_both(layout, n)
                    right_width = bottom_height = n * 2 * node_radius + (n - 1) * spacing
                elif n_group == 2:
                    layout = easl.utils.Graph.flipped_layout_vertical(layout, n)
                    right_width = max(right_width, n * 2 * node_radius + (n - 1) * spacing)
                    top_height = max(top_height, n * 2 * node_radius + (n - 1) * spacing)
                elif n_group == 3:
                    layout = easl.utils.Graph.flipped_layout_both(layout, n)
                    left_width = max(left_width, n * 2 * node_radius + (n - 1) * spacing)
                    bottom_height = max(bottom_height, n * 2 * node_radius + (n - 1) * spacing)

                for node in group:
                    grid_x, grid_y = layout.pop()

                    coordinates[node] = (node_radius + grid_x * spacing, node_radius + grid_y * spacing)

            width = left_width + right_width
            height = top_height + bottom_height

        surface = pygame.Surface((width, height))
        surface.fill(self.BG_COLOR)

        # Draw edges from stored coordinates
        for a, b in graph.edges:
            ax, ay = coordinates[a]
            bx, by = coordinates[b]
            pygame.draw.line(surface, self.FG_COLOR, coordinates[a], coordinates[b])

            # Draw arrow heads
            if ax == bx:
                cx = bx
                cy = by - node_radius if by > ay else by + node_radius
            elif ay == by:
                cx = bx - node_radius if bx > ax else bx + node_radius
                cy = by
            else:
                dx = ax - bx
                dy = ay - by
                angle = math.atan2(-dy, dx)

                delta_x = node_radius * math.cos(angle)
                delta_y = node_radius * math.sin(angle)

                cx = int(bx + delta_x)
                cy = int(by - delta_y)

            pygame.draw.circle(surface, self.FG_COLOR, (cx, cy), 4)

        for node in coordinates:
            x, y = coordinates[node]

            pygame.draw.circle(surface, self.OBJ_COLOR, (x, y), node_radius)
            name = self.font.render(node, 1, self.FG_COLOR)
            surface.blit(name, (x, y))

        return surface

    def __draw_rows(self, rows):
        # Draw every element, take its size and draw the next after it
        elements = []
        h = 0
        max_w = 0

        margin = pygame.Surface((8, 1))

        # Find the dimensions of the surface
        for element in rows.get_elements():
            elements.append(margin)
            h += margin.get_height()

            e = self.__draw_visualization(element)
            elements.append(e)

            max_w = max(max_w, e.get_width())
            h += e.get_height()

        # Blit to surface
        surface = pygame.Surface((max_w, h))
        surface.fill(PyGameVisualizer.BG_COLOR)

        y = 0
        for e in elements:
            surface.blit(e, (0, y))

            y += e.get_height()

        return surface
