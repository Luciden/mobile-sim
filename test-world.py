__author__ = 'Dennis'

from easl import *


def count(self):
    c = self.a["count"]
    self.try_change("count", c + 1 if c < 10 else 0)


def count_emission(self):
    return [Signal("number", "count", self.a["count"], range(10))]


class CountSensor(Sensor):
    def init(self):
        self.signals.update({"count": range(10)})
        self.default_signals.update({"count": 0})

    def detects_modality(self, modality):
        return modality == "number"

if __name__ == '__main__':
    counter = Entity("counter")
    counter.add_attribute("count", 0, range(10), None)
    counter.set_physics(count)
    counter.set_emission(count_emission)

    viewer = Entity("viewer")
    viewer.add_attribute("count", 0, range(10), None)
    viewer.add_sensor(CountSensor())

    world = World()
    world.add_entity(counter)
    world.add_entity(viewer)

    world.run(100)

