# 
version = '0.0'

class Object:
    """
    Anything in the environment that can change state
    in some way.
    """
    def addActuator(self):
        """
        An actuator can get activated by an Action.
        """
    
    def addDynamics(self):
        """
        Dynamics specify how the object behave over
        time.
        """

class Actor:
    """
    Object that can also perform actions.
    These actions then influence the environment in some way.
    """
    
    def addAction(self):
        """
        An Action is something that can both change an
        actor's internal state and activate another
        Object's 
        """

class Experimenter:
    """
    Plays back a recording of kicking behavior.
    """
    
class Experiment:
    """
    Handles everything in the experiment environment, including
    object creation and data collection.
    """
    def __init__(self):
        pass
    
    def run(self):
        """
        
        """
        running = True
        while(running):
            # perform all object's internal dynamics
            # calculate actions and actuate actuators
            # repeat

class Agent:
    """
    Interface for different types of agents that control
    an Actor.
    
    Specification of the actor has to be matched to the
    agent's internal representation.
    """
    def __init__(self):
        pass
    