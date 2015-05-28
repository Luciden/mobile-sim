__author__ = 'Dennis'

import random
from copy import copy, deepcopy

from easl.controller import Controller
from easl.utils import stat
from easl.visualize import *


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
    actions : [name]
        List of names of predicates that are actions.
    """
    NOW = 0
    PREV = -1
    FUT = 1

    def __init__(self, actions=None):
        if actions is None:
            actions = []

        self._MAX_AGE = 8

        self._SENSORY = 0
        self._ACTION = 1
        self.oldest = 0

        self.actions = actions

        self.memory = {}
        self.__init_now()

    def __init_now(self):
        self.memory[0] = ([], [])

    def add_sensory(self, predicate):
        """
        Adds a sensory predicate.
        """
        self.memory[0][self._SENSORY].append(predicate)

    def add_action(self, action):
        """
        Adds an action predicate.
        """
        self.memory[0][self._ACTION].append(action)

    def age(self):
        """
        Updates all memory units' age by one time step.
        """
        # Create a new representation with all ages incremented
        # by going from the oldest (maximum i) to newest and
        # shifting up one (m[i+1] = m[i])
        for i in range(len(self.memory) - 1, -1, -1):
            if i == self._MAX_AGE:
                # Delete the entry from memory
                del self.memory[i]
            else:
                self.memory[i + 1] = self.memory[i]
                self.oldest = i + 1

        self.__init_now()

    def get_oldest(self):
        return self.oldest

    def get_of_age(self, age):
        """
        Get all predicates of the specified age.

        Returns
        -------
        [Predicate]
        """
        if age > self.oldest:
            return []

        predicates = []
        predicates.extend(self.memory[age][self._ACTION])
        predicates.extend(self.memory[age][self._SENSORY])

        return predicates

    def has_predicate(self, age, predicate):
        if age not in self.memory:
            return False

        for p in self.memory[age][self._SENSORY]:
            if p == predicate:
                return True
        for p in self.memory[age][self._ACTION]:
            if p == predicate:
                return True
        return False

    def matches_now(self, temporal, now=0):
        """
        Returns
        -------
        bool
            True if the temporal predicates match now, t=0, False otherwise
        """
        prev = now + 1

        time = {WorkingMemory.NOW: now,
                WorkingMemory.PREV: prev}

        # Try to match the temporal predicates
        for (p, t) in temporal:
            # Always match actions if they can be satisfied now
            if p.name in self.actions and now == 0 and t == WorkingMemory.NOW:
                continue

            if t not in time:
                return False
            if not self.has_predicate(time[t], p):
                return False

        return True

    @staticmethod
    def __is_tag_possible(match, age, tag):
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
    """
    Attributes
    ----------
    name : string
        Name of the predicate.
    value : value
    """
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __eq__(self, other):
        if isinstance(other, Predicate):
            return self.name == other.name and self.value == other.value

    def __str__(self):
        return "%s(%s)" % (self.name, str(self.value))


class Conjunction(object):
    """
    Temporally tagged conjunctions of predicates.
    """
    def __init__(self, temporal=None):
        """
        Attributes
        ----------
        predicates : [(Predicate, tag)]
            Temporal predicates that form the conjunction.
        """
        if temporal is None:
            self.predicates = []
        else:
            self.predicates = [temporal]

    def __eq__(self, other):
        if isinstance(other, Conjunction) and len(self.predicates) == len(other.predicates):
            # Check if all predicates are in the other conjunction too
            # i.e. if the intersection of predicates is the same as the current set
            for (p, t) in self.predicates:
                if (p, t) not in other.predicates:
                    return False

            return True
        else:
            return False

    def __str__(self):
        return ', '.join(['%s'] * len(self.predicates)) % tuple([(str(p), t) for (p, t) in self.predicates])

    def add_predicate(self, predicate, tag):
        if not self.has_predicate(predicate, tag):
            self.predicates.append((predicate, tag))

    def has_predicate(self, predicate, tag):
        for p, t in self.predicates:
            if p == predicate and t == tag:
                return True

        return False

    def get_temporal(self):
        return self.predicates

    def get_predicates(self):
        return [p for (p, _) in self.predicates]

    def has_predicate_with_name_from(self, predicates, tag):
        for (p, t) in self.predicates:
            if p.name in predicates and t == tag:
                return True
        return False

    def get_predicates_with_name_from(self, predicates):
        return [(p, t) for (p, t) in self.predicates if p.name in predicates]

    def is_strict_subset_of(self, other):
        if not isinstance(other, Conjunction):
            raise RuntimeError("Can only compare two Conjunctions.")

        if not len(self.predicates) < len(other.predicates):
            return False

        for (p, t) in self.predicates:
            if not other.has_predicate(p, t):
                return False

        return True

    @staticmethod
    def combine(a, b):
        new = Conjunction()

        for (p, t) in a.predicates:
            new.add_predicate(p, t)
        for (p, t) in b.predicates:
            new.add_predicate(p, t)

        return new


class Reinforcer(object):
    """
    Attributes
    ----------
    predicate : Predicate
        Predicate that states which variable/value pair is considered to be
        rewarding.
    conjunctions : [(Conjunction, int, int)]]
        Keeps for every conjunction how many times it was satisfied and how
        many times it was followed by this reinforcer respectively.
    predictors : [Conjunction]
        Temporal predicate that predicts the reinforcer with its associated
        probability.
    """
    def __init__(self, predicate):
        self.predicate = predicate

        # Start with the null conjunction
        self.conjunctions = []
        self.add_conjunction(Conjunction())

        self.predictors = []

    def add_conjunction(self, conjunction, satisfied=False, followed=False):
        s = 1 if satisfied else 0
        f = 1 if followed else 0

        # Only add if the conjunction is not already in the table
        for (c, sc, fc) in self.conjunctions:
            if c == conjunction:
                return

        self.conjunctions.append((conjunction, s, f))

    def increment_conjunctions(self, memory):
        """
        Updates all conjunctions that are currently being watched.

        Parameters
        ----------
        predicates : [Predicate]
        """
        for i in range(len(self.conjunctions)):
            conjunction, s, f = self.conjunctions[i]
            # If the conjunction is matched by taking the most future tag as t=0,
            # increment satisfied.
            if memory.matches_now(conjunction.get_temporal(), 1):
                # If the conjunction is matched by taking the most future tag as t=-1
                # increment followed if predicate is true at t=0
                if memory.has_predicate(0, self.predicate):
                    self.conjunctions[i] = (conjunction, s + 1, f + 1)
                else:
                    self.conjunctions[i] = (conjunction, s + 1, f)

    def count(self, conjunction):
        """
        Parameters
        ----------
        conjunction : Conjunction

        Returns
        -------
        (number, number)
            the number of times the conjunction was satisfied since reinforcer
            acquisition and the number of times the conjunction was satisfied
            since acquisition.
        """
        for (c, s, f) in self.conjunctions:
            if c == conjunction:
                return s, f

    def find_best_conjunctions(self):
        """
        Returns
        -------
        best_conjunctions : [Conjunction]
        """
        # If less than two conjunctions, include all
        if len(self.conjunctions) < 2:
            return [c for (c, s, f) in self.conjunctions]

        # for conjunctions:
        rr = []
        rc = []

        for (_, s, f) in self.conjunctions:
            if s == 0:
                rr.append(0)
            else:
                rr.append(f / s)
            rc.append(f)

        # Calculate mean reward rate and standard deviation
        m_rr = stat.mean(rr)
        std_rr = stat.pstdev(rr)

        # Calculate mean reward count and standard deviation
        m_rc = stat.mean(rc)
        std_rc = stat.pstdev(rc)

        # Filter generated conjunctions on those with rates or counts of one
        # standard deviation above mean
        best = [c
                for (c, s, f)
                in self.conjunctions
                if s != 0 and float(f) / float(s) > m_rr + std_rr
                or f > m_rc + std_rc]
        return best

    def get_predictors(self):
        return deepcopy(self.predictors)

    def create_predictor(self):
        # Add new predictors
        for predictor in self.__create_predictor():
            self.__add_predictor(predictor)

    def __add_predictor(self, predictor):
        for p in self.predictors:
            if p == predictor:
                return
        self.predictors.append(predictor)

    def remove_predictor(self, predictor):
        self.predictors[:] = [p for p in self.predictors if not p == predictor]

    def __create_predictor(self):
        """

        Returns
        -------
        predictors : [Conjunction]
        """
        # "New predictors are created from the best-scoring conjunctions currently
        # maintained for that reinforcer.
        # "When creating new predictors, candidate conjunctions are sorted by merit
        # rather than raw reward rate to give greater weight to conjunctions that
        # have been sampled more heavily."
        # "If there are still several candidates, two are chosen at random to become
        # new predictors." (Enforces exploration.)
        conjunctions = sorted([(c, n, r) for (c, n, r) in self.conjunctions],
                              key=lambda x: Reinforcer.merit(x[2], x[1]),
                              reverse=True)

        if len(conjunctions) == 0:
            return []
        if len(conjunctions) <= 2:
            return [c for (c, n, r) in conjunctions]

        # "If several conjunctions are tied for top score, the ones with the fewest
        # number of terms are selected."
        top = []
        top_conjunction, top_n, top_r = conjunctions[0]
        top_score = Reinforcer.merit(top_r, top_n)

        for c, n, r in conjunctions:
            if abs(Reinforcer.merit(r, n) - top_score) <= 1e-6:
                top.append(c)

        if len(top) > 2:
            return sorted(top, key=lambda x: len(x.predicates))[:1]
        else:
            return top

    @staticmethod
    def merit(r, n):
        """
        .. math:: M(r, n) = \frac{r}{n} \mdot \max(0.2, 1 - \frac{1.175}{n})
        .. math:: M(r, 0) = 1
        """
        if n == 0:
            return 0
        else:
            return (r / float(n)) * max(0.2, 1 - (1.175 / float(n)))

    @staticmethod
    def demerit(r, n):
        """
        .. math:: D(r, n) = \min(1, \frac{r}{n} + \frac{n - r}{0.7n^2})
        .. math:: D(r, 0) = 0
        """
        if n == 0:
            return 1
        else:
            return min(1, (r / float(n)) + (n - r) / float(0.7 * n ** 2))


class OperantConditioningVisual(Visual):
    @staticmethod
    def visualize(self):
        group = Group("operant")
        group.add_element(List("actions", [str(a) for a in self.selected_actions]))
        for reinforcer in self.reinforcers:
            r = Group("reinforcer")
            r.add_element(Number("reinforcer", str(reinforcer.predicate)))
            r.add_element(List("predictors", [str(c) for c in reinforcer.predictors]))
            r.add_element(List("conjunctions", [(str(c), s, f) for (c, s, f) in reinforcer.conjunctions]))

            group.add_element(r)
            
        return group


class OperantConditioningController(Controller):
    """Uses operant conditioning based learning.

    Attributes
    ----------
    actions : {name: [value]}
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
    observations : [(name, value)]
    selected_actions : [(name, value)]
        For debugging purposes.

    References
    ----------
    .. [1] "Operant Conditioning in Skinnerbots,"
           David S. Touretzky & Lisa M. Saksida.
    """
    def __init__(self):
        super(OperantConditioningController, self).__init__(visual=OperantConditioningVisual())
        self.observations = []

        self.memory = None
        self.reinforcers = []

        self.selected_actions = []

        self._DEMERIT_THRESHOLD = 0.5
        self._SUFFICIENT_TRIALS = 10
        self._SIMILAR_MERIT_THRESHOLD = 0.2

    def init_internal(self, entity):
        super(OperantConditioningController, self).init_internal(entity)

        self.memory = WorkingMemory(actions=self.actions.keys())

        # Add all actions as predictors
        for reinforcer in self.reinforcers:
            for action in self.actions:
                for value in self.actions[action]:
                    reinforcer.add_conjunction(Conjunction((Predicate(action, value), WorkingMemory.NOW)))

    def sense(self, observation):
        """
        Parameters
        ----------
        observation : (name, value)
        """
        # Store observations for later conversion
        self.observations.append(observation)

    def act(self):
        self.memory.age()
        self.__store_observations()

        self.__acquire_reinforcers()
        self.__generate_conjunctions()

        self.__update_reinforcer_counts()

        # "New predictors for a given reinforcer are created only when that
        #  reinforcer has just been received and the reward counts updated.
        #  At that point, the program can check candidate predictors against its
        #  working memory, so that it only constructs predictors that would have
        #  predicted the reward it just got."
        self.__create_predictors()
        self.__delete_predictors()

        actions = self.__select_actions()
        if len(actions) == 0:
            actions = [self.__select_random_action()]

        self.selected_actions = copy(actions)

        # Add actions as predicates
        for action in actions:
            self.log.do_log("observation", {"controller": "operant", "name": action[0], "value": action[1]})
            self.memory.add_action(Predicate(action[0], action[1]))

        return actions

    def set_primary_reinforcer(self, name, value):
        primary = Reinforcer(Predicate(name, value))
        self.reinforcers.append(primary)

    def __store_observations(self):
        """Stores all observations as sensory predicates.
        """
        for (name, value) in self.observations:
            self.memory.add_sensory(Predicate(name, value))

        # Clear for the next iteration
        self.observations = []

    def __update_reinforcer_counts(self):
        # increment all reinforcer/conjunction occurrences for the new
        # observations
        for reinforcer in self.reinforcers:
            reinforcer.increment_conjunctions(self.memory)

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
            best_conjunctions = reinforcer.find_best_conjunctions()
            # Find best predicates, i.e. best conjunctions of 1 predicate

            best_predicates = [c for c in best_conjunctions
                               if len(c.predicates) == 1]

            if len(best_predicates) == 0:
                best_predicates = self.__derive_temporal_predicates()

            for c in best_conjunctions:
                for p in best_predicates:
                    reinforcer.add_conjunction(Conjunction.combine(c, p))

    def __derive_temporal_predicates(self):
        """
        "The algorithm for inferring reinforcement contingencies operates on a
         collection of slightly more abstract items called temporal predicates.
         These are derived from working memory elements by replacing numeric
         time tags with symbolic labels."

         Returns
         -------
         [(Predicate, tag)]
            Temporal predicates.
        """
        # Take the previous time step as a point of reference and create the
        # temporal predicates.
        predicates = []

        for p in self.memory.get_of_age(1):
            predicates.append(Conjunction((p, WorkingMemory.NOW)))

        prev = self.memory.get_of_age(2)
        for p in prev:
            predicates.append(Conjunction((p, WorkingMemory.PREV)))

        return predicates

    def __create_temporal_action_predicates(self):
        predicates = []

        for action in self.actions:
            for value in self.actions[action]:
                predicates.append((Predicate(action, value), WorkingMemory.NOW))

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
        # "Furthermore, in order for new predictors to be created the reward must
        #  either have been unexpected, meaning the current set of predictors is
        #  incomplete, or there must have been at least one false prediction since
        #  the last reward was encountered, meaning there is an erroneous predictor,
        #  one that is not specific enough to accurately express the reward
        #  contingencies."
        # Check if the current set of predictors is incomplete.
        # I.e. unexpected reward, or reward but no prediction.
        reinforced = []
        renew = []  # all reinforcers that should have new predictors created

        # Check if there were any incomplete predictors
        # i.e. any unexpected rewards
        for predicate in self.memory.get_of_age(0):
            if self.__has_acquired_reinforcer(predicate):
                reinforcer = self.__get_reinforcer(predicate)
                reinforced.append(reinforcer)
                if len(self.__was_predicted(reinforcer)) == 0:
                    # Create new predictors for the reinforcer
                    renew.append(reinforcer)

        # For all reinforcers that are not already being renewed
        # Check if false prediction of reward. (Erroneous predictor.).
        for reinforcer in self.reinforcers:
            if reinforcer not in reinforced:
                # See if predictor actually predicted it
                if len(self.__was_predicted(reinforcer)) > 0:
                    # Create new predictors for the reinforcer
                    renew.append(reinforcer)

        for reinforcer in renew:
            reinforcer.create_predictor()

    def __was_predicted(self, reinforcer):
        """

        Parameters
        ----------
        reinforcer : Reinforcer

        Returns
        -------
        [Conjunction]
            All predictors that predicted the reinforcer to occur at the
            current time.
        """
        # Check for all predictors for reward if it was predicted.
        predictors = []
        for predictor in reinforcer.predictors:
            # Check if the predictor could have matched one time step before
            if self.memory.matches_now(predictor.get_temporal(), 1):
                predictors.append(predictor)
        return predictors

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
        # Get all reinforcers that were just reinforced
        reinforced = []
        for predicate in self.memory.get_of_age(0):
            if self.__has_acquired_reinforcer(predicate):
                reinforced.append(self.__get_reinforcer(predicate))

        # false alarm (reward predicted, but no reward)
        # delete if demerit below threshold
        for reinforcer in self.reinforcers:
            # Only check reinforcers that were not predicted
            if reinforcer not in reinforced:
                predicted_by = self.__was_predicted(reinforcer)
                if len(predicted_by) > 0:
                    # Delete if demerit below threshold
                    for predictor in predicted_by:
                        n, r = reinforcer.count(predictor)

                        if Reinforcer.demerit(r, n) < self._DEMERIT_THRESHOLD:
                            reinforcer.remove_predictor(predictor)

        # if predictor successful
        # delete if demerit is lower than highest merit of other successful predictor
        for reinforcer in self.reinforcers:
            if reinforcer in reinforced:
                predicted_by = self.__was_predicted(reinforcer)
                if len(predicted_by) > 0:
                    for conjunction in predicted_by:
                        s, f = reinforcer.count(conjunction)
                        demerit = Reinforcer.demerit(f, s)
                        highest_predictor, highest_merit = None, 0
                        # Find merits of successful predictors
                        for predictor in reinforcer.predictors:
                            if predictor == conjunction:
                                continue

                            n, r = reinforcer.count(predictor)
                            merit = Reinforcer.merit(r, n)
                            if merit > highest_merit:
                                highest_predictor = predictor
                                highest_merit = merit

                            if highest_predictor is not None:
                                if demerit < merit:
                                    reinforcer.remove_predictor(conjunction)

        # if there is a predictor with:
        #  - antecedent strict subset of this predictor
        #  - merit nearly as good
        #  - number of trials sufficiently high to have reasonable confidence of
        #    equivalence
        # delete
        for reinforcer in self.reinforcers:
            for predictor in reinforcer.predictors:
                n, r = reinforcer.count(predictor)
                merit_predictor = Reinforcer.merit(r, n)

                # Number of trials sufficiently high to have confidence of equivalence?
                if n < self._SUFFICIENT_TRIALS:
                    continue

                # Try to find another predictor that satisfies the requirements
                for other in reinforcer.predictors:
                    if other == predictor:
                        continue
                    n, r = reinforcer.count(other)
                    merit_other = Reinforcer.merit(r, n)

                    # Number of trials sufficiently high to have confidence of equivalence?
                    if n < self._SUFFICIENT_TRIALS:
                        continue

                    # Antecedent strict subset of this predictor?
                    # Merit nearly as good?
                    if other.is_strict_subset_of(predictor) and \
                       abs(merit_predictor - merit_other) < self._SIMILAR_MERIT_THRESHOLD:
                        reinforcer.remove_predictor(predictor)

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
                # reinforcer, add the reinforcer if it does not already exist.
                for (sensory, tag) in predictor.get_predicates_with_name_from(self.sensory.keys()):
                    if not self.__has_acquired_reinforcer(sensory):
                        self.reinforcers.append(Reinforcer(sensory))
                        self.log.do_log("reinforcer", {"controller": "operant", "predicate": sensory.name, "value": sensory.value})

    def __select_actions(self):
        """Selects actions by matching predictors with the working memory.

        "To generate behavior, we look for predictors that can be satisfied by the
        rat's taking some action currently available to it."

        "At each time step, the skinnerbot seeks a predictor it can satisfy.
         Predictors are prioritized by the nature of the reinforcement they
         promise, so that given a choice, the skinnerbot will always act to secure
         a more basic reward (water) over a more abstract one (the ability to
         press the bar.)
         If it finds a predictor where all but one of the predicates is currently
         true (i.e., matches an item in working memory), and the last one can be
         made true by taking some action that is presently available, then it will
         select that action with high probability.
         There is also some randomness in the action selection mechanism, to
         facilitate exploration."

         Returns
         -------
         [(name, value)]
            List of action names and valuesRANDOM
        """
        matches = []

        # Find predictors that can be satisfied
        for reinforcer in self.reinforcers:
            for predictor in reinforcer.predictors:
                temporal = predictor.get_temporal()
                if self.memory.matches_now(temporal):
                    matches.append(temporal)

        # If all sensory predicates in a predictor are true (match items in
        # working memory), and there is an action predicate that is available,
        # the action will be selected with high probability.
        #
        # Find the action predicates in the match that can be satisfied now
        actions = []
        for match in matches:
            for (p, tag) in match:
                if p.name in self.actions.keys() and tag == WorkingMemory.NOW:
                    actions.append(p)

        # Select one of the matched actions randomly
        if len(actions) == 0:
            return []
        else:
            action = random.choice(actions)
            return [(action.name, action.value)]

    def __select_random_action(self):
        print "RANDOM"
        action = random.choice(self.actions.keys())
        value = random.choice(self.actions[action])

        return action, value

    def __has_acquired_reinforcer(self, predicate):
        """
        Checks whether the predicate is considered to be a reinforcer.

        Parameters
        ----------
        predicate : Predicate
        """
        for reinforcer in self.reinforcers:
            if reinforcer.predicate == predicate:
                return True
        return False

    def __get_reinforcer(self, predicate):
        """
        Parameters
        ----------
        predicate : Predicate
        """
        for reinforcer in self.reinforcers:
            if reinforcer.predicate == predicate:
                return reinforcer
        raise RuntimeError("Reinforcer not found.")
