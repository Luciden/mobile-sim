__author__ = 'Dennis'

from easl import *

def lamp_physics(self):
    self.try_action("on", not self.a["on"])

def lamp_emission(self):
    s = []
    if self.a["on"]:
        s.append(Signal("sight", "light", 1))

    return s

def step2():
    lamp = Entity()
    lamp.add_attribute("on", False)
    lamp.set_physics(lamp_physics)

    world = World()
    world.add_entity("lamp", lamp)

    world.run()

class LampSensor(Sensor):
    def detects_modality(self, modality):
        return modality == "sight"

    def notify(self, signal):
        if signal.modality == "sight":
            if signal.type == "light":
                self.observations["light"] = True

def step3():
    world = World()

    lamp = Entity()
    lamp.add_attribute("on", False)
    lamp.set_physics(lamp_physics)
    lamp.add_sensor(LampSensor())
    lamp.set_emission(lamp_emission)

    lamp2 = Entity()
    lamp2.add_attribute("on", False)
    lamp2.set_physics(lamp_physics)
    lamp2.add_sensor(LampSensor())
    lamp2.set_emission(lamp_emission)

    world.add_entity("lamp", lamp)
    world.add_entity("lamp2", lamp2)

    world.run()

def step4():
    def move_up(self):
        self.try_action("position", "up")

    def move_down(self):
        self.try_action("position", "down")

    arm = Entity()
    arm.add_attribute("position", "down")
    arm.add_action("move-up", move_up)
    arm.add_action("move-down", move_down)

    def moved(self, direction):
        self.a["position"] = direction

    ball = Entity()
    ball.add_attribute("position", "down")
    ball.add_trigger("move", moved)

    world = World()
    world.add_entity("arm", arm)
    world.add_entity("ball", ball)

    world.run()

if __name__ == '__main__':
    print "Run step 2:"
    print "Single Entity that changes over time."
    step2()

    print 3 * "\n"

    print "Run step 3:"
    print "Two Entities that change over time, where the Entities observe/sense each other."
    # TODO(Dennis): Get it to work so that light: False is also observed.
    step3()

    print 3 * "\n"

    print "Run step 4:"
    print "Two Entities that change each others state through interacting."
    step4()
