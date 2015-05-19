
"""
Containing the experiment based on the mobile experiment.
"""
import functools

from easl import *
from easl.controller import *
from easl.visualize import Visualizer


#
# Infant functions
#

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


def new_position(position, direction):
    if direction == "still" or direction == "up" and position == "up" or direction == "down" and position == "down":
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


def relative_direction(self, value, attribute):
    """
    Callback function for the infant's limbs.
    """
    self.try_change(attribute, new_position(self.a[attribute], value))


def move(old, new):
    return "movement", {"direction": calc_direction(old, new)}


#
# Mobile functions
#

def swing(self):
    speed = self.a["speed"]
    if 0 < speed <= 10:
        self.try_change("speed", speed - 1)
    if speed > 10:
        self.try_change("speed", 10)


def moved(self, direction):
    self.a["previous"] = self.a["speed"]
    self.a["speed"] += 4


def movement_emission_boolean(self):
    s = []
    if self.a["speed"] > 0:
        s.append(Signal("sight", "movement", True, [True, False]))

    return s


def movement_emission_change(self):
    s = []

    if self.a["speed"] == 0:
        s.append(Signal("sight", "movement", "idle", ["idle", "faster", "slower", "same"]))
    elif self.a["speed"] > self.a["previous"]:
        s.append(Signal("sight", "movement", "faster", ["idle", "faster", "slower", "same"]))
    elif self.a["speed"] < self.a["previous"]:
        s.append(Signal("sight", "movement", "slower", ["idle", "faster", "slower", "same"]))
    else:
        s.append(Signal("sight", "movement", "same", ["idle", "faster", "slower", "same"]))

    return s


class SightSensorBoolean(Sensor):
    def init(self):
        self.signals.update({"movement": [True, False]})
        self.default_signals.update({"movement": False})

    def detects_modality(self, modality):
        return modality == "sight"


class SightSensorChange(Sensor):
    def init(self):
        self.signals.update({"movement": ["idle", "faster", "slower", "same"]})
        self.default_signals.update({"movement": "idle"})

    def detects_modality(self, modality):
        return modality == "sight"


def create_infant(agent):
    """
    Parameters
    ----------
    controller : string
        Name of the type of controller to use.
    """
    infant = Entity("infant")

    if agent == "random":
        infant.set_agent(RandomController())
    elif agent == "operant":
        infant.set_agent(OperantConditioningController())
        infant.agent.set_primary_reinforcer("movement", "faster")
    elif agent == "causal":
        cla = CausalLearningController()
        cla.set_values({"movement": "faster"})
        infant.set_agent(cla)
    else:
        raise RuntimeError("Undefined controller type.")

    infant.add_attribute("left-hand-position", "down", ["down", "middle", "up"], move)
    infant.add_attribute("right-hand-position", "down", ["down", "middle", "up"], move)
    infant.add_attribute("left-foot-position", "down", ["down", "middle", "up"], move)
    infant.add_attribute("right-foot-position", "down", ["down", "middle", "up"], move)

    infant.add_action("left-hand",
                      ["up", "still", "down"],
                      "still",
                      functools.partial(relative_direction, attribute="left-hand-position"))

    infant.add_action("right-hand",
                      ["up", "still", "down"],
                      "still",
                      functools.partial(relative_direction, attribute="right-hand-position"))

    infant.add_action("left-foot",
                      ["up", "still", "down"],
                      "still",
                      functools.partial(relative_direction, attribute="left-foot-position"))

    infant.add_action("right-foot",
                      ["up", "still", "down"],
                      "still",
                      functools.partial(relative_direction, attribute="right-foot-position"))

    infant.add_sensor(SightSensorChange())

    return infant


def create_mobile_boolean():
    mobile = Entity("mobile")

    mobile.add_attribute("speed", 0, range(0, 10), lambda old, new: None)
    mobile.set_physics(swing)

    mobile.add_trigger("movement", moved)
    mobile.set_emission(movement_emission_boolean)

    return mobile


def create_mobile_change():
    mobile = Entity("mobile")

    mobile.add_attribute("speed", 0, range(0, 10), lambda old, new: None)
    mobile.add_attribute("previous", 0, range(0, 10), lambda old, new: None)

    mobile.set_physics(swing)

    mobile.add_trigger("movement", moved)
    mobile.set_emission(movement_emission_change)

    return mobile


def create_experimenter(experiment_log):
    """
    Parameters
    ----------
    log : Log
        Log to play back kicking behavior from.
    """
    experimenter = Entity("experimenter")
    # second argument is dictionary of which actions of the original log match which actions.
    agent = LogController("infant", experiment_log)
    agent.set_watched("right-foot-position", "mechanical-hand", calc_direction)
    experimenter.set_agent(agent)

    experimenter.add_attribute("mechanical-hand-position", "down", ["down", "middle", "up"], move)

    experimenter.add_action("mechanical-hand",
                            ["up", "still", "down"],
                            "still",
                            functools.partial(relative_direction, attribute="mechanical-hand-position"))

    return experimenter


def experimental_condition(n):
    infant = create_infant("causal")
    mobile = create_mobile_change()

    world = World()
    world.add_entity(infant)
    world.add_entity(mobile)
    world.set_area_of_effect("infant", "right-foot-position", "movement", "mobile")

    world.run(n)

    return world.log


def control_condition(n, experiment_log):
    infant = create_infant("causal")
    mobile = create_mobile_change()
    experimenter = create_experimenter(experiment_log)

    world = World()
    world.add_entity(infant)
    world.add_entity(mobile)
    world.add_entity(experimenter)
    world.set_area_of_effect("experimenter", "mechanical-hand-position", "movement", "mobile")

    world.run(n)

    return world.log


if __name__ == '__main__':
    log = experimental_condition(100)

    v = Visualizer()
    v.visualize(log)

    # log2 = control_condition(n, log)

    # v.visualize(log2)
