"""
An Experiment consists of a collection of Actors (entities) that
interact with each other in some way.
An Actor can either change because of internal mechanisms, or
because of interactions with another Actor.

Internal:
    Rules specify how the Actor's state changes every time step.

External:
    If a Trigger is triggered, this might change an Actor's state.

Action:
    An Actor can perform an Action that might trigger Triggers in
    another Actor.

Actors' Actions and Triggers can be linked to create the dynamics
of the experiment.
"""
version = '0.0'

class Agent:
    """
    Interface for different types of agents that control
    an Actor.
    
    Specification of the actor has to be matched to the
    agent's internal representation.
    """
    def __init__(self):
        pass

class IdleAgent(Agent):
    def act(self):
        return []

class Actor:
    """
    Any entity in the environment that can act and/or be acted on.
    """
    def __init__(self):
        self.triggers = {}
        self.dynamics = pass
        self.controller = IdleAgent()
        
        self.triggered = []
        self.acted     = []
    
    def addAction(self, name):
        """
        An Action is something that can both change an
        actor's internal state and activate another
        Object's 
        """
        self.name = name
    
    def addTrigger(self, name, event):
        """
        event: function that is called for this Actor when the
                trigger is triggered
        """
        if not self.triggers.has_key(name):
            self.triggers[name] = event
        else
            pass
    
    def setDynamics(self, dynamics):
        self.dynamics = dynamics
    
    def tick(self):
        """
        Is called every time step in an experiment.
        Defines how the Actor's internal state changes without
        regarding interaction with other Actors.
        """
        self.dynamics(self)
    
    def trigger(self, trigger):
        if self.triggers.has_key(trigger):
            self.triggers[trigger](self)
            
    
    def setController(self, agent):
        self.controller = agent
    
    def act(self):
        """
        Gives which Actions the Actor performs this time step.
        """
        return self.controller.act()
    
    def sense(self):
        """
        Passes information to the Agent
        """
        # To the associated Agent
        # Pass a list of all actions
        # and a list of all triggered triggers
        self.controller.sense()
    

class Experiment:
    """
    Handles everything in the experiment environment, including
    object creation and data collection.
    """
    def __init__(self):
        self.maxSteps = 1000
        self.actors = {}
        self.links = {}
        """
        {
        X : {
            a1 : [(Y, t1)],
            a2 : [(Y, t3), (Z, t4)]
            },
        Y : {
            a3 : [(X, t1)]
            }
        }
        """
    
    def run(self):
        """
        Runs one experiment with the current settings, objects
        and rules.
        """
        step = 0
        while(step < maxSteps):
            for a in self.actors:
                self.actors[a].tick()
            # calculate actions and actuate actuators
            for a in self.actors:
                if self.links.has_key(a):
                    actions = self.actors[a].act()
                    link = self.links[a]
                    for action in actions:
                        if link.has_key(action):
                            for trigger in link[action]:
                                self.actors[trigger[1]].trigger(trigger[2])
                else:
                    pass
            
            step += 1
    
    def addActor(self, actor):
        # Only add new actors if they do not already exist
        if self.actors.has_key(actor):
            print 'Already has actor'
        else:
            self.actors[actor] = Actor(actor)
    
    def addLink(self, sender, action, receiver, trigger):
        """
        link: list of two two-tuples of format
              [ (actorname, actionname), (actorname, trigger) ]
        """
        # add link to currently existing links
        if self.links.has_key(sender):
            self.links[sender].append( (action, receiver, trigger) ))
        else:
            self.links[sender] = [ (action, receiver, trigger) ]
        
    