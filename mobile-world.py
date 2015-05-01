"""
Containing the experiment based on the mobile experiment.
"""
from easl import *


class SightSensor(Sensor):
    def detects_modality(self, modality):
        return modality == "sight"

    def notify(self, signal):
        if signal.sig_type == "movement":
            self.observations["movement"] = True

if __name__ == '__main__':
    infant = Entity()
    infant.add_attribute("left-hand-position", "down")
    infant.add_attribute("right-hand-position", "down")
    infant.add_attribute("left-foot-position", "down")
    infant.add_attribute("right-foot-position", "down")

    infant.add_action("left-hand-up", lambda self: self.try_action("left-hand-position", "up"))
    infant.add_action("left-hand-down", lambda self: self.try_action("left-hand-position", "down"))

    infant.add_action("right-hand-up", lambda self: self.try_action("right-hand-position", "up"))
    infant.add_action("right-hand-down", lambda self: self.try_action("right-hand-position", "down"))

    infant.add_action("left-foot-up", lambda self: self.try_action("left-foot-position", "up"))
    infant.add_action("left-foot-down", lambda self: self.try_action("left-foot-position", "down"))

    infant.add_action("right-foot-up", lambda self: self.try_action("right-foot-position", "up"))
    infant.add_action("right-foot-down", lambda self: self.try_action("right-foot-position", "down"))

    infant.add_sensor(SightSensor())

    mobile = Entity()
    def swing(self):
        if self.a["speed"] > 0:
            self.a["speed"] -= 1

    def moved(self, direction):
        self.a["speed"] += 10

    mobile.add_attribute("speed", 0)
    mobile.set_physics(swing)

    mobile.add_trigger("moved", moved)

    world = World()
    world.add_entity("infant", infant)
    world.add_entity("mobile", mobile)

    world.run(10)
