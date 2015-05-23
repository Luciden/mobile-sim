__author__ = 'Dennis'

import pygame


class Slider(object):
    """
    A slider with a number of positions.

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


class Table(object):
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


class Visualizer(object):
    FG_COLOR = (255, 255, 255)

    def __init__(self):
        pygame.init()

        self.size = 640, 640
        self.screen = None

    def visualize(self, log):
        # TODO: Make automatic layout-manager
        # TODO: Add into actual simulation (real-time visualizing)
        # TODO: Implement visualizer interface in Entity and Controller
        """
        Parameters
        ----------
        log : Log
            The data to visualize.
        """
        # Get the information from entities
        self.screen = pygame.display.set_mode(self.size)
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
                        self.__draw_limb("left-hand-position", m["left-hand-position"], (16, 16))
                        self.__draw_limb("right-hand-position", m["right-hand-position"], (128, 16))
                        self.__draw_limb("left-foot-position", m["left-foot-position"], (16, 128))
                        self.__draw_limb("right-foot-position", m["right-foot-position"], (128, 128))

            time += 1
            pygame.display.flip()
            pygame.time.delay(100)

    def __draw_limb(self, name, value, position):
        p = 0
        if value == "up":
            p = 0
        elif value == "middle":
            p = 1
        elif value == "down":
            p = 2

        self.__draw_slider(Slider(name, 3, p), position)

    def __draw_slider(self, slider, position):
        x, y = position
        slider_w = 4
        block_w = 32

        length = slider.number * block_w

        center_x = x + block_w / 2 - slider_w / 2
        block_y = (length / float(slider.number)) * slider.position

        length = slider.number * block_w

        # Draw the name on top
        font = pygame.font.SysFont("monospace", 11)
        name = font.render(slider.name, 1, (255, 255, 255))
        self.screen.blit(name, position)

        # Draw the slider base
        pygame.draw.rect(self.screen, Visualizer.FG_COLOR, [center_x, y + 16, 4, length])

        # Draw the slider block
        pygame.draw.rect(self.screen, Visualizer.FG_COLOR, [x, y + 16 + block_y, block_w, block_w])
