import mobile-sim
"""
How to handle changes in each time step?
"""

class OperantConditioningAgent():
    def act(self):
        # To be implemented
        return []

infant = Actor("infant")

infant.addAction("left-foot")
infant.addAction("right-foot")
infant.addAction("left-hand")
infant.addAction("right-hand")

infant.addTrigger("see-movement", def see(self): self.see = True )

mobile = Actor("mobile")
mobile.addAction("move")
mobile.addTrigger("prodded", def move (self): self.speed += 10 )

exp = Experiment()
exp.addActor(infant)
exp.addActor(mobile)

exp.addLink("infant", "right-foot", "mobile", "prodded")
exp.addLink("mobile", "move", "infant", "see-movement")

# how to handle Agents?
exp.setController("infant", OperantConditioningAgent())

exp.run()
