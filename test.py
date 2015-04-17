import mobile-sim

"""
"""
infant = Actor("infant")

infant.addAction("leftfoot")
infant.addAction("rightfoot")
infant.addAction("lefthand")
infant.addAction("righthand")

mobile = Object("mobile")
mobile.addActuator("prodded", def move (self): self.speed += 10 )

exp = Experiment()
exp.addActor(infant)
exp.addObject(mobile)

# dict['name']
exp.connect( {'infant': 'rightfoot', 'mobile': 'prodded'} 

# How to make infant observe the mobile?
# How to handle changes in each time step?

infant.sees(mobile)

