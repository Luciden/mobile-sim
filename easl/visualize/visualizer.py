__author__ = 'Dennis'

import pygame


class Visualizer(object):
    def __init__(self):
        pygame.init()

        self.size = 640, 640
        self.screen = None

    def visualize(self, log):
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
                        self.__draw_limb("right-hand-position", m["right-hand-position"], (64, 16))
                        self.__draw_limb("left-foot-position", m["left-foot-position"], (16, 320))
                        self.__draw_limb("right-foot-position", m["right-foot-position"], (64, 320))

            time += 1
            pygame.display.flip()
            pygame.time.delay(100)

    def __draw_limb(self, name, value, position):
        x, y = position

        LIMB_COLOR = (255, 255, 255)

        pygame.draw.rect(self.screen, LIMB_COLOR, [x, y, 4, 256])
        if value == "up":
            pygame.draw.rect(self.screen, LIMB_COLOR, [x - 16, y, 32, 32])
        elif value == "middle":
            pygame.draw.rect(self.screen, LIMB_COLOR, [x - 16, y + 96, 32, 32])
        elif value == "down":
            pygame.draw.rect(self.screen, LIMB_COLOR, [x - 16, y + 224, 32, 32])

