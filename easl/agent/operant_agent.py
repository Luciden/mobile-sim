__author__ = 'Dennis'

import random
from copy import deepcopy

from agent import Agent
from easl.utils import stat

NOW = 0
PREV = -1
FUT = 1


class WorkingMemory(object):
    """
    "The working memory module holds a collection of time-labeled
         predicates describing the rat's current perceptions and actions
         and those of the recent past."

    Attributes
    ----------
    memory : {number: ([predicates], [predicates])}
         Age, sensory predicates, and action predicates at the current,
         and recent, instant(s).
    """

    def __init__(self):
        self._MAX_AGE = 8

        self.memory = {}
        self.__init_now()

    def __init_now(self):
        self.memory[0] = ([], [])

    def age(self):
        """
        Updates all memory units' age by one time step.
        """
        # Create a new representation with all ages incremented.
        aged = {}
        for m in self.memory:
            aged[m + 1] = self.memory[m]

        self.memory = aged
        # Prepare the current time slot
        self.__init_now()

    def add_sensory(self, predicate):
        """
        Adds a sensory predicate.
        """
        self.memory[0][0].append(predicate)

    def add_action(self, action):
        """
        Adds an action predicate.
        """
        self.memory[0][1].append(action)

    def get_of_age(self, age):
        return deepcopy(self.memory[age])

    def has_predicate(self, age, predicate):
        for p in self.memory[age]:
            if p == predicate:
                return True
        return False

    def is_match(self, predictor, offset=0):
        """
        Determines whether there is a mapping of predicates to temporal tags
        such that the predictor's set of predicates is a subset of the set
        of predicates in the mapping.

        Parameters
        ----------
        predictor : Predictor
            predictor to be matched against the memory

        Returns
        -------
        bool
            True if a match is found, False otherwise
        """
        # TODO: Not finished yet, probably.
        # First check if all sensory predicates can be matched
        possible, match = self.__is_match_rec([], predictor.get_sensory_temporal(), offset)

        return possible

    def __is_match_rec(self, match, predicates, offset):
        """
        Parameters
        ----------
        match : [(predicate, age, tag)]
            match so far
        predicates : [Predicate]
            still unmatched predicates
        offset : number
            offset in age from which to ignore (used to check previous state)
        """
        if len(predicates) == 0:
            return True, match

        predicate, tag = predicates[0]

        for i in range(offset, self._MAX_AGE):
            if self.has_predicate(i, predicate):
                # see if we can assign the tag taking into account previously
                # matched predicates
                if self.__is_tag_possible(match, i, tag):
                    new = deepcopy(match)
                    new.append((predicate, i, tag))

                    # Use the tag, but keep going if this does not match all
                    if self.__is_match_rec(new, predicates[1:]):
                        return True, match

        return False, []

    def __is_tag_possible(self, match, age, tag):
        """

        Parameters
        ----------
        match
            matched predicates so far
        age
            age for the new predicate
        tag
            which tag the new predicate is going to be tagged with
        """
        for (_, a, t) in match:
            if age - a != tag - t:
                return False
        return True


class Predicate(object):
    def __init__(self, name, vals):
        self.name = name
        self.vals = vals

    def __eq__(self, other):
        if isinstance(Predicate, other) and other.name == self.name:
            # All same parameters
            self_set = set(self.vals.keys())
            other_set = set(other.vals.keys())

            if len(self_set - other_set) != 0 or len(other_set - self_set) != 0:
                return False

            # Same predicates if there are no different values
            return len(set(o for o in self_set if self.vals[o] != other.vals[o])) == 0
        else:
            return False


class Conjunction(object):
    def __init__(self):
        self.predicates = set()

    def __eq__(self, other):
        if isinstance(Conjunction, other):
            # Check if all predicates are in the other conjunction too
            # i.e. if the intersection of predicates is the same as the current set
            return len(self.predicates.intersection(other.predicates)) == len(self.predicates)
        else:
            return False

    def add_predicate(self, predicate):
        self.predicates.add(predicate)


class Predictor(object):
    def __init__(self):
        self.sensory = []
        self.action = []

    def add_sensory_predicate(self, predicate):
        """
        Parameters
        ----------
        predicate : (Predicate, string)
            temporal predicate
        """
        self.sensory.append(predicate)

    def add_action_predicate(self, predicate):
        self.action.append(predicate)

    def get_sensory_predicates(self):
        """
        Take the sensory predicates in this predictor and strip them from the
        temporal tags.
        """
        return [p for (p, _) in self.sensory]

    def get_action_predicates(self):
        """
        Take the action predicates in this predictor and strip them from the
        temporal tags.
        """
        return [p for (p, _) in self.action]

    def get_sensory_temporal(self):
        return self.sensory

    def get_action_temporal(self):
        return self.action


class Reinforcer(object):
    def __init__(self, predicate):
        self.predicate = predicate

        # Start with the null conjunction
        self.conjunctions = []
        self.add_conjunction(Conjunction())

        self.predictors = []

    def inc_satisfied(self, conjunction):
        """
        Increments the number of times the conjunction was satisfied since this
        reinforcer was acquired.

        Returns
        -------
        bool
            True if the conjunction was already found, False otherwise
        """
        # Find the conjunction and increment it
        for i in range(len(self.conjunctions)):
            if self.conjunctions[i][0] == conjunction:
                self.conjunctions[i][1] += 1
                return True

        self.__add_conjunction(conjunction, satisfied=True)
        return False

    def __add_conjunction(self, conjunction, satisfied=False, followed=False):
        s = 1 if satisfied else 0
        f = 1 if followed else 0
        self.conjunctions.append((conjunction, s, f))

    def inc_followed(self, conjunction):
        """
        Increments the number of times the conjunction's occurrence was followed
        by the reinforcer.
        """
        for i in range(len(self.conjunctions)):
            if self.conjunctions[i][0] == conjunction:
                self.conjunctions[i][2] += 1
                return True

        self.__add_conjunction(conjunction, followed=True)
        return False

    def count(self, conjunction):
        """
        Returns
        -------
        (number, number)
            the number of times the conjunction was satisfied since reinforcer
            acquisition and the number of times the conjunction was satisfied
            since acquisition.
        """
        for c in self.conjunctions:
            if c[0] == conjunction:
                return c[1], c[2]

    def reward_rate(self, conjunction):
        s, f = self.count(conjunction)

        if s == 0:
            raise ZeroDivisionError()

        return f / s

    def best_conjunctions(self):
        # for conjunctions:
        rr = []
        rc = []

        for (_, s, f) in self.conjunctions:
            rr.append(s / f)
            rc.append(f)

        # Calculate mean reward rate and standard deviation
        m_rr = stat.mean(rr)
        std_rr = stat.pstdev(rr)

        # Calculate mean reward count and standard deviation
        m_rc = stat.mean(rc)
        std_rc = stat.pstdev(rc)

        # Filter generated conjunctions on those with rates or counts of one
        # standard deviation above mean
        return [c
                for (c, s, f)
                in self.conjunctions
                if float(s) / float(f) > m_rr + std_rr
                or f > m_rc + std_rc]

    def get_predictors(self):
        return deepcopy(self.predictors)

    @staticmethod
    def merit(r, n):
        """
        .. math:: M(r, n) = \frac{r}{n} \mdot \max(0.2, 1 - \frac{1.175}{n})
        .. math:: M(r, 0) = 1
        """
        if n == 0:
            return 1
        else:
            return (r / n) * max(0.2, 1 - (1.175 / float(n)))

    @staticmethod
    def demerit(r, n):
        """
        .. math:: D(r, n) = \min(1, \frac{r}{n} + \frac{n - r}{0.7n^2})
        .. math:: D(r, 0) = 0
        """
        if n == 0:
            return 0
        else:
            return min(1, (r / n) + (n - r) / (0.7 * n ** 2))


class OperantConditioningAgent(Agent):
    # TODO(Dennis): Implement.
    """
    Uses operant conditioning based learning.

    Primary reinforcers can reinforce behavior without the animal having had
    any prior experience with them (e.g., food, water).

    Needs
     - link between action predicates and actual actions

    References
    ----------
    .. [1] "Operant Conditioning in Skinnerbots,"
           David S. Touretzky & Lisa M. Saksida.
    """
    # TODO(Question): Where to get primary reinforcers?
    # TODO: When to create new reinforcer?
    # TODO: When new reinforcer, create new predictor.

    def __init__(self):
        """
        Attributes
        ----------
        reinforcers : [ {predicate: [conjunction: (sat, fol)]} ]
            "Conditioned reinforcers are stimuli that become associated with food or
             water (or some other innate reward (even exercise), and serve as a signal
             that the reward is coming, thereby eliminating the gap between the desired
             action and the reinforcement signal."
            "In order to extract this information from its experience of the
             world, the program maintains two tables for each reinforcer.
             One counts the number of times each conjunction has been satisfied
             since that reinforcer was acquired; the other table counts the
             number of times a conjunction's occurrence has been followed on
             the next time step by the reinforcer.
        predictors : [(reinforcer, conjunction, probability)]
            All current predictors.
        """
        super(OperantConditioningAgent, self).__init__()
        self.memory = WorkingMemory()

        self.reinforcers = []
        self.predictors = []

        self.observations = []

        self.best_predicates = []

        self.actions = {}

    def init_internal(self, actions):
        # TODO: Implement.
        # Create action and observable predicates
        self.actions = actions
        # TODO: What are the initial reinforcers?
        pass

    def sense(self, observation):
        # Store observations for later conversion
        self.observations.append(observation)

    def act(self):
        self.memory.age()
        # Turn observations into predicates
        self.__store_observations()

        self.__acquire_reinforcers()
        self.__generate_conjunctions()

        self.__update_reinforcer_counts()

        # TODO: generate when reinforcers have been received
        self.__generate_predictors()

        actions = self.__select_actions()
        # Add actions as predicates
        for action in actions:
            self.memory.add_action(action)

        return actions

    def set_primary_reinforcer(self, predicate):
        self.reinforcers.append(Reinforcer(predicate))

    def __store_observations(self):
        """
        Stores all observations as sensory predicates.
        """
        for observation in self.observations:
            self.memory.add_sensory(observation)

        # Clear for the next iteration
        self.observations = []

    def __update_reinforcer_counts(self):
        # TODO: Implement.
        observed = self.memory.get_of_age(0)
        previous = self.memory.get_of_age(1)

        # increment all reinforcer/conjunction occurrences for the new
        # observations
        # TODO: Get conjunctions instead of predicates.
        for conjunction in observed:
            for reinforcer in self.reinforcers:
                reinforcer.inc_satisfied(conjunction)

        # if there are any reinforcers for the current instant, increment
        # the values for all conjunctions that were followed by it in the
        # last timestep.
        for conjunction in observed:
            # for any reinforcer in the conjunction
            for reinforcer in self.reinforcers:
                if reinforcer in observed:
                    # increment the followed for the reinforcer/conjunction
                    for x in previous:
                        reinforcer.inc_followed(conjunction)

    def __generate_conjunctions(self):
        """
        Conjunctions are constructed incrementally by combining a pool of
        currently "best" conjunctions (starting with the null conjunction)
        with a pool of "best" predicates.

        A "best" conjunction is one whose reward rate is at least one standard
        deviation above the mean rate, or whose reward count is at least one
        standard deviation above the mean count. Both tests are necessary.
        """
        # Calculate for every reinforcer separately
        for reinforcer in self.reinforcers:
            # Combine previously 'best' conjunctions with predicates and check
            # which conjunctions are 'best' next
            predicates = self.__derive_temporal_predicates()
            best_conjunctions = reinforcer.__find_best_conjunctions()

            for c in best_conjunctions:
                for p in predicates:
                    new_c = deepcopy(c)
                    new_c.add_predicate(deepcopy(p))

                    reinforcer.add_conjunction(new_c)
                    # TODO: Reinforcer should increment its own conjunctions.

    def __derive_temporal_predicates(self):
        """
        "The algorithm for inferring reinforcement contingencies operates on a
         collection of slightly more abstract items called temporal predicates.
         These are derived from working memory elements by replacing numeric
         time tags with symbolic labels."
        """
        # Take the previous time step as a point of reference and create the
        # temporal predicates.
        predicates = []

        future = self.memory.get_of_age(0)
        now = self.memory.get_of_age(1)
        previous = self.memory.get_of_age(2)

        for p in future:
            predicates.append((p, FUT))
        for p in now:
            predicates.append((p, NOW))
        for p in previous:
            predicates.append((p, PREV))

        return predicates

    def __create_predictors(self):
        """
        Predictor: conjunction -> reinforcer w/ probability

        "During learning, conjunctions that are sufficiently well correlated with
         rewards generate "predictors," i.e., rules for predicting reward.
         These may displace earlier predictors that have not performed as well.
         To allow for the effects of noise, predictors are not replaced until they
         have a reasonably high application count (so their success rate can be
         accurately estimated) and their replacement has a significantly higher success
         rate."

        Predictor Creation and Deletion

        "New predictors for a given reinforcer are created only when that reinforcer
         has just been received and the reward counts updated.
         At that point, the program can check candidate predictors against its
         working memory, so that it only constructs predictors that would have
         predicted the reward it just got."
        "Furthermore, in order for new predictors to be created the reward must
         either have been unexpected, meaning the current set of predictors is
         incomplete, or there must have been at least one false prediction since
         the last reward was encountered, meaning there is an erroneous predictor,
         one that is not specific enough to accurately express the reward
         contingencies."

        "Two numerical measures are used to assign scores to conjunctions and
         predictors: merit and demerit.
         They estimate the lower and upper bounds, respectively, on the true reward
         rate based on the number of examples seen so far."

        "Let :math:`n` be the number of times a conjunction has been observed to be
         true, and :math:`r` the number of times the reinforcer was received on the
         subsequent time step.
         Merit and demerit are defined as:"

        .. math:: M(r, n) = \frac{r}{n} \mdot \max(0.2, 1 - \frac{1.175}{n})
        .. math:: M(r, 0) = 1

        .. math:: D(r, n) = \min(1, \frac{r}{n} + \frac{n - r}{0.7n^2})
        .. math:: D(r, 0) = 0

        "As :math:`n` approaches :math:`\inf`, merit and demerit both converge to
         :math:`\frac{r}{n}`, the true reward rate."


         When deleting predictors, demerit is used, so the program is conservative
         in its judgements and does not delete too quickly."
        """
        # TODO: Implement
        # Check if predictors incomplete. (Unexpected reward. Reward but no prediction.)
        reinforced = []
        renew = []  # all reinforcers that should have new predictors created

        # For all reinforcers that appear now
        for predicate in self.memory.get_of_age(0):
            if self.__has_acquired_reinforcer(predicate):
                reinforcer = self.__get_reinforcer(predicate)
                reinforced.append(reinforcer)
                if not self.__was_predicted(reinforcer):
                    # Create new predictors for the reinforcer
                    renew.append(reinforcer)

        # Find all reinforcers that were not found yet
        # Check if false prediction of reward. (Erroneous predictor.).
        for reinforcer in self.reinforcers:
            if reinforcer not in reinforced:
                # See if predictor actually predicted it.
                if self.__was_predicted(reinforcer):
                    # Create new predictors for the reinforcer
                    renew.append(reinforcer)

    def __create_predictor(self, reinforcer):
        # "New predictors are created from the best-scoring conjunctions currently
        # maintained for that reinforcer.
        # "When creating new predictors, candidate conjunctions are sorted by merit
        # rather than raw reward rate to give greater weight to conjunctions that
        # have been sampled more heavily."
        # If several conjunctions are tied for top score, the ones with the fewest
        # number of terms are selected."
        # "If there are still several candidates, two are chosen at random to become
        # new predictors." (Enforces exploration.)
        # TODO: Implement.
        # Calculate merit for every conjunction.
        # Choose with highest merit.
        conjunctions = [(c, Reinforcer.merit(r, n)) for (c, n, r) in reinforcer.conjunctions]

        pass


    def __was_predicted(self, reinforcer):
        # Check for all predictors for reward if it was predicted.
        for predictor in reinforcer.predictors:
            # Check if the predictor could have matched one time step before
            success, match = self.memory.is_match(predictor, 1)

            if success:
                return True
        return False

    def __delete_predictors(self):
        """
        "Predictors are deleted in three circumstances.

         First, if the predictor has just given a false alarm, it may be deleted if
         its demerit is below a certain minimum value. (Remove bad predictors.)
         Second, if a reinforcer has just been correctly predicted, the predictor
         may be deleted if its demerit is less than the highest merit of any other
         successful predictor for that reinforcer. (Substitution for better one.)
         Finally, a predictor will be deleted if there is another predictor whose
         antecedent uses a strict subset of the terms in this predictor's
         conjunction, whose merit is nearly as good, and whose number of trials is
         sufficiently high that there is reasonable confidence that the two
         predictors are equivalent.
        """
        # false alarm (reward predicted, but no reward)
        # delete if demerit below threshold

        # if predictor successful
        # delete if demerit is lower than highest merit of other successful predictor

        # if there is a predictor with:
        #  - antecedent strict subset of this predictor
        #  - merit nearly as good
        #  - number of trials sufficiently high to have reasonable confidence of
        #    equivalence
        # delete
        pass

    def __acquire_reinforcers(self):
        """
        Acquiring Conditioned Reinforcers

        "If the skinnerbot could find a way to make HEAR(pump) be true, then
         predictor #3 suggests it could get water whenever it wanted.
         So HEAR(pump) becomes a secondary reinforcer, and the skinnerbot begins
         trying out theories of what causes the pump to run."

        I.e. if a predictor has a sensory predicate, that sensory predicate
        becomes a reinforcer itself.
        """
        for reinforcer in self.reinforcers:
            for predictor in reinforcer.get_predictors():
                # if there is a sensory predicate that is not already a
                # reinforcer, add the reinforcer.

                for sensory in predictor.get_sensory_predicates():
                    if not self.__has_acquired_reinforcer(sensory):
                        self.reinforcers.append(sensory)

    def __select_actions(self):
        """
        Action Generation

        "To generate behavior, we look for predictors that can be satisfied by the
        rat's taking some action currently available to it."

        "At each time step, the skinnerbot seeks a predictor it can satisfy.
         Predictors are prioritized by the nature of the reinforcement they\
         promise, so that given a choice, the skinnerbot will always act to secure
         a more basic reward (water) over a more abstract one (the ability to
         press the bar.)
         If it finds a predictor where all but one of the predicates is currently
         true (i.e., matches an item in working memory), and the last one can be
         made true by taking some action that is presently available, then it will
         select that action with high probability.
         There is also some randomness in the action selection mechanism, to
         facilitate exploration."
        """
        # TODO(Question): Use a different mechanism (i.e. not random) for exploration?
        # Check predictors to see which can be satisfied.
        # Prioritized by nature of the reinforcement.
        # (Number denoting primary, secondary, etc?)
        matches = []

        # TODO: Store matches (tag mappings) together with predictors, to later check actions.
        for reinforcer in self.reinforcers:
            for predictor in reinforcer.predictors:
                if self.memory.is_match(predictor):
                    matches.append(predictor)

        # If all sensory predicates in a predictor are true (match items in
        # working memory), and there is an action predicate that is available,
        # the action will be selected with high probability.
        #
        # So filter on matches with action predicates.
        # TODO: Filter only on those with actions NOW.
        matches = [p for p in matches if len(p.get_action_predicates()) != 0]

        # Select one of the matches with probability
        # ? (There is also some randomness to facilitate exploration.)
        selected = random.choice(matches)

        return selected.get_action_predicates()

    def __has_acquired_reinforcer(self, predicate):
        for reinforcer in self.reinforcers:
            if reinforcer.predicate == predicate:
                return True
        return False

    def __get_reinforcer(self, predicate):
        for reinforcer in self.reinforcers:
            if reinforcer.predicate == predicate:
                return reinforcer
        raise RuntimeError("Reinforcer not found.")
