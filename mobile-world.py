"""
Containing the experiment based on the mobile experiment.
"""
import functools

from easl import *
from easl.agent import RandomAgent
from easl.agent import OperantConditioningAgent
from easl.agent import CausalLearningAgent


def calc_direction(a, b):
    """
    Calculates which direction b is from a.
    """
    d = {"down": -1, "middle": 0, "up": 1}

    if d[a] == d[b]:
        return "still"
    if d[a] < d[b]:
        return "up"
    if d[a] > d[b]:
        return "down"


def relative_direction(self, direction, attribute):
    self.try_change(attribute, new_position(self.a[attribute], direction))


class SightSensor(Sensor):
    def detects_modality(self, modality):
        return modality == "sight"

    def notify(self, signal):
        if signal.sig_type == "movement":
            self.observations["movement"] = True

if __name__ == '__main__':
    infant = Entity()
    #infant.set_agent(RandomAgent())
    #infant.set_agent(OperantConditioningAgent())
    #infant.agent.set_primary_reinforcer("movement", {"value": True})
    infant.set_agent(CausalLearningAgent())

    def move(old, new):
        return "movement", {"direction": calc_direction(old, new)}

    infant.add_attribute("left-hand-position", "down", move)
    infant.add_attribute("right-hand-position", "down", move)
    infant.add_attribute("left-foot-position", "down", move)
    infant.add_attribute("right-foot-position", "down", move)

    def new_position(position, direction):
        if direction == "up" and position == "up" or direction == "down" and position == "down":
            # Already at maximum, so nothing changes
            return position
        elif direction == "up":
            if position == "down":
                return "middle"
            if position == "middle":
                return "up"
        elif direction == "down":
            if position == "up":
                return "middle"
            if position == "middle":
                return "down"

        raise RuntimeError("Unhandled movement {1} from {0}.".format(position, direction))

    infant.add_action("left-hand",
                      {"direction": ["up", "down"]},
                      functools.partial(relative_direction, attribute="left-hand-position"))

    infant.add_action("right-hand",
                      {"direction": ["up", "down"]},
                      functools.partial(relative_direction, attribute="right-hand-position"))

    infant.add_action("left-foot",
                      {"direction": ["up", "down"]},
                      functools.partial(relative_direction, attribute="left-foot-position"))

    infant.add_action("right-foot",
                      {"direction": ["up", "down"]},
                      functools.partial(relative_direction, attribute="right-foot-position"))

    infant.add_sensor(SightSensor())

    mobile = Entity()

    def swing(self):
        speed = self.a["speed"]
        if 0 < speed <= 30:
            self.try_change("speed", speed - 1)
        if speed > 30:
            self.try_change("speed", 30)

    def moved(self, direction):
        self.a["speed"] += 10

    mobile.add_attribute("speed", 0, lambda old, new: None)
    mobile.set_physics(swing)

    mobile.add_trigger("movement", moved)

    world = World()
    world.add_entity("infant", infant)
    world.add_entity("mobile", mobile)
    world.set_area_of_effect("infant", "right-foot-position", "movement", "mobile")

    world.run(10)
