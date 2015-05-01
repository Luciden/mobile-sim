import mobile-sim
"""
How to handle changes in each time step?
"""

class InfantOCAgent(OperantConditioningAgent):
    def __init__(self):
        OperantConditioningAgent.__init__(self)
        
        self.actionTable = {
            "left-foot": "move-left-foot",
            "left-hand": "move-left-hand",
            "right-foot": "move-right-foot",
            "right-hand": "move-right-hand"
        }
        
        self.addReinforcer("see-movement")
        self.addAction("move-left-foot")
        self.addAction("move-right-foot")
        self.addAction("move-left-hand")
        self.addAction("move-right-hand")
    
    def sense(self, actions, triggers):
        ageMemory(self)
        
        for a in actions:
            self.addMemory(self.actionTable[a])
        
        for t in triggers:
            if t == "see-movement"
            self.addMemory("see-movement")


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
