
"""
Containing the experiment based on the mobile experiment.
"""
import functools
import argparse

from easl import *
from easl.mechanisms import *
from easl.visualize import *


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


def move_limb(old, new):
    return "movement", {"direction": calc_direction(old, new)}


#
# Mobile functions
#

def swing_direction(self):
    v = self.a["velocity"]
    p = self.a["position"]
    d = self.a["direction"]
    self.a["previous"] = self.a["velocity"]

    if d == "+":
        p_new = p + v
        if p_new <= 10:
            self.try_change("position", p_new)
        else:
            self.try_change("position", 10 - (p_new - 10))
            self.try_change("direction", "-")
    elif d == "-":
        p_new = p - v
        if p_new >= 0:
            self.try_change("position", p_new)
        else:
            self.try_change("position", abs(p_new))
            self.try_change("direction", "+")
    else:
        raise RuntimeError("HUH?")

    # Decay
    self.try_change("velocity", max(0, min(v - 1, 10)))


def moved_direction(self, direction):
    ignore_direction = True

    if ignore_direction:
        self.a["velocity"] = min(self.a["velocity"] + 3, 10)
    else:
        if self.a["direction"] == "+":
            self.a["velocity"] = 3
        elif self.a["direction"] == "-":
            self.a["velocity"] = min(self.a["velocity"] + 3, 10)
        self.a["direction"] = "-"


def movement_emission_change(self):
    s = []

    if self.a["velocity"] == 0:
        s.append(Signal("sight", "movement", "idle", ["idle", "faster", "slower"]))
    elif self.a["velocity"] > self.a["previous"]:
        s.append(Signal("sight", "movement", "faster", ["idle", "faster", "slower"]))
    elif self.a["velocity"] < self.a["previous"]:
        s.append(Signal("sight", "movement", "slower", ["idle", "faster", "slower"]))
    else:
        s.append(Signal("sight", "movement", "slower", ["idle", "faster", "slower"]))

    return s


class SightSensorChange(Sensor):
    def init(self):
        self.signals.update({"movement": ["idle", "faster", "slower"]})
        self.default_signals.update({"movement": "idle"})

    def detects_modality(self, modality):
        return modality == "sight"


class InfantVisual(Visual):
    @staticmethod
    def visualize(self):
        p = {"up": 0, "middle": 1, "down": 2}

        grid = Grid("infant", 2, 2)

        grid.add_element(Slider("left-hand-position", 3, p[self.a["left-hand-position"]]), 0, 0)
        grid.add_element(Slider("right-hand-position", 3, p[self.a["right-hand-position"]]), 0, 1)
        grid.add_element(Slider("left-foot-position", 3, p[self.a["left-foot-position"]]), 1, 0)
        grid.add_element(Slider("right-foot-position", 3, p[self.a["right-foot-position"]]), 1, 1)

        return grid


def infant_new_causal_controller():
    controller = CausalLearningMechanism()
    controller.set_rewards({"movement": "faster"})
    controller.add_ignored(["movement"])
    controller.set_motor_signal_bias(infant_action_valuation_constant, 0.5)
    controller.set_considered_signals(["left-foot", "right-foot", "left-hand", "right-hand"])
    controller.set_considered_sensory(["left-foot-position", "right-foot-position", "left-hand-position", "right-hand-position"])

    return controller


def infant_new_simple_controller():
    controller = OperantConditioningMechanism([("movement", "faster")])
    controller.set_motor_signal_bias(infant_action_valuation_single_limb, 1.0)
    return controller


def create_infant():
    """
    Parameters
    ----------
    mechanisms : string
        Name of the type of mechanisms to use.
    """
    infant = Entity("infant", visual=InfantVisual())

    infant.add_attribute("left-hand-position", "middle", ["down", "middle", "up"], move_limb)
    infant.add_attribute("right-hand-position", "middle", ["down", "middle", "up"], move_limb)
    infant.add_attribute("left-foot-position", "middle", ["down", "middle", "up"], move_limb)
    infant.add_attribute("right-foot-position", "middle", ["down", "middle", "up"], move_limb)

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


def infant_action_valuation(signals):
    """
    Parameters
    ----------
    signals : dict
    """
    count = 0

    for signal in signals:
        if signals[signal] == "still":
            count += 1

    return max(count / float(4), 0.1)


def infant_action_valuation_move_n_limbs(n, signals):
    still = 0

    for signal in signals:
        if signals[signal] == "still":
            still += 1

    moving = 4 - still

    if 0 < moving <= n:
        return 1.0
    else:
        return 0.0


def infant_action_valuation_single_limb(signals):
    return infant_action_valuation_move_n_limbs(1, signals)


def infant_action_valuation_two_limbs(signals):
    return infant_action_valuation_move_n_limbs(2, signals)


def infant_action_valuation_constant(signals):
    return 1.0


class MobileDirectionVisual(Visual):
    @staticmethod
    def visualize(self):
        group = Group("mobile")
        group.add_element(Number("velocity", self.a["velocity"]))
        # Invert the slider (direction down is up)
        group.add_element(Slider("position", 11, 10 - self.a["position"]))
        group.add_element(Circle("velocity", 0, 10, self.a["velocity"]))

        return group


def create_mobile_direction():
    mobile = Entity("mobile", visual=MobileDirectionVisual())

    mobile.add_attribute("position", 5, range(0, 10), lambda old, new: None)
    mobile.add_attribute("velocity", 0, range(0, 10), lambda old, new: None)
    mobile.add_attribute("previous", 0, range(0, 10), lambda old, new: None)
    mobile.add_attribute("direction", "+", ["+", "-"], lambda old, new: None)

    mobile.set_physics(swing_direction)

    mobile.add_trigger("movement", moved_direction)
    mobile.set_emission(movement_emission_change)

    return mobile


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # parser.add_argument("-q", "--quiet", help="when specified, text output to the console is suppressed (not implemented yet)",
    #                     action="store_true")
    parser.add_argument("-V", "--visualizer", help="when specified, the simulation is visualized using PyGame",
                        action="store_true")
    parser.add_argument("mechanism", type=str, help="specify the mechanism to be used",
                        choices=["operant_conditioning", "causal_learning"])
    parser.add_argument("condition", type=str, help="specify which condition to simulate",
                        choices=["normal", "switch_halfway"])
    args = parser.parse_args()

    visualize = args.visualizer

    mechanism = args.mechanism
    condition = args.condition

    ss = SimulationSuite()
    if visualize:
        ss.set_visualizer(PyGameVisualizer())
    ss.set_simulation_length(300)
    ss.set_data_bins(6)
    ss.add_constant_entities({"infant": create_infant, "mobile": create_mobile_direction})
    ss.add_controllers("infant", {"operant_conditioning": infant_new_simple_controller, "causal_learning": infant_new_causal_controller})

    ss.add_initial_triggers({"experimental": [("infant", "right-foot-position", "movement", "mobile")]})
    ss.add_conditional_trigger_changes({"experimental": {"normal": ([], []),
                                                         "switch_halfway": ({150: [("infant", "left-hand-position", "movement", "mobile")]},
                                                                            {150: [("infant", "right-foot-position", "movement", "mobile")]})}})

    ss.add_constant_data_collection(["left-hand-position", "right-hand-position", "left-foot-position", "right-foot-position"], ["lh", "rh", "lf", "rf"])

    run_single = True
    make_average = True
    if run_single:
        ss.run_single("experimental", condition, {"infant": mechanism})
    else:
        ss.run_simulations()
