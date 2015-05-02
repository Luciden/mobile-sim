class OperantConditioningAgent(Agent):
    """
    Memory is a list of predicates with their age (timesteps since observation).
    """
    PREV = -1
    NOW = 0
    FUT = 1
    
    def __init__(self):
        self.memorySize = 8
        self.memory = []
        
        self.reinforcers = []
        """
        {
        R : { C1 : (sat, fol, rr), C2 : (sat, fol, rr), C3..}
        }
        """
        self.actions = []
        self.observations = []
    
    def addMemory(self, m):
        self.memory.append( (m, 0) )

    def addAction(self, name):
        self.actions.append(name)
    
    def addReinforcer(self, name):
        """
        Add tables for the new reinforcer without conjunctions.
        """
        if not self.reinforcers.has_key(name):
            self.reinforcers[name] = {}
    
    def ageMemory(self):
        for m in range(len(self.memory)):
            if self.memory[m][1] >= self.maxAge:
                del self.memory[m]
            else:
                self.memory[m][1] += 1
    
    def init(self):
        """
        Called when the experiment starts.
        """
        # Initialize the conjunctions
        for k in keys(self.reinforcers):
            for c in createConjunctions(self.actions + self.observations):
                self.reinforcers[k].append
    
    def createConjunctions(p):
        """
        Create all possible conjunctions of a list of propositions.
        
        p: list of strings
        """
        return powerset(p)
    
    def powerset(seq):
        """
        Modified from: http://www.technomancy.org/python/powerset-generator-python/
        Doesn't return the empty set.
        
        Yields all the subsets of this set. This is a generator.
        """
        if len(seq) <= 1:
            yield seq
            yield []
        else:
            for item in powerset(seq[1:]):
                yield [seq[0]]+item
                yield item
        
