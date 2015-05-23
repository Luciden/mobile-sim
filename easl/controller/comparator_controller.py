__author__ = 'Dennis'

from controller import Controller


class State(object):
    def __init__(self):
        """
        A state, used for desired, actual and predicated states.

        Models the perception that is now, is predicted, or was.
        """
    pass


class Comparator(object):
    def __init__(self):
        """
        Interface for a comparator in the comparator model.

        Compares two objects of State and returns some kind of feedback.
        """
        pass

    @staticmethod
    def compare(state_a, state_b):
        """

        """
        raise NotImplementedError("The Comparator base class should not be used.")


class InverseModel(object):
    def __init__(self):
        """
        Interface for an inverse model of action/motor signals to state.
        """
        pass

    def inverse(self, desired):
        """
        Parameters
        ----------
        desired : State
            The desired state.

        Returns
        -------
        motor_signals : [(name, value)]
            The motor signals that should be produced to achieve the desired
            state of perception.
        """
        raise NotImplementedError("The InverseModel base class should not be used.")

    def update(self, error):
        pass


class ForwardModel(object):
    def __init__(self):
        """
        Interface for a forward model of action/motor signals to predicted state.
        """
        pass

    def predict(self, motor_signals):
        """
        Parameters
        ----------
        motor_signals : {string: value}
            Names and values of the motor signals from which to predict.

        Returns
        -------
        perception : State
            The predicted state of perception.
        """
        raise NotImplementedError("The ForwardModel base class should not be used.")

    def update(self, error):
        pass


class ComparatorController(Controller):
    """
    Uses sensorimotor learning based on the comparator mechanism.

    Needs
     - unknown
    """
    def __init__(self, controller, predictor, comparator1, comparator2, comparator3):
        """
        Attributes
        ----------
        controller : InverseModel
            An inverse model, from desired state to motor commands
        predictor : ForwardModel
        comparator1: Comparator
            Between desired and (estimated) actual states.
        comparator2: Comparator
            Between desired and predicted states.
        comparator3: Comparator
            Between predicted and (estimated) actual states.
        """
        super(ComparatorController, self).__init__()

        self.controller = controller
        self.predictor = predictor

        self.comparator1 = comparator1
        self.comparator2 = comparator2
        self.comparator3 = comparator3

        self.actual_state = None
        self.desired_state = None
        self.predicted_state = None

    def init_internal(self, entity):
        super(ComparatorController, self).init_internal(entity)

    def sense(self, observation):
        raise NotImplementedError("Hmm.")

    def act(self):
        # Make/get desired State (calculate from some kind of assumption?)
        # TODO: Where do you get the desired state?
        desired_state = State()
        # Get (estimated) actual State (calculate from observations)
        actual_state = self.actual_state

        # Update the predictor with feedback from the comparator
        self.predictor.update(self.comparator3.compare(actual_state, self.predicted_state))

        # Get motor commands from desired state
        motor_signals = self.controller.inverse(desired_state)

        # Calculate the predicted state from the motor signals
        predicted_state = self.predictor.predict(motor_signals)

        # Update the forward and inverse models with feedback from comparators
        self.controller.update(self.comparator2.compare(desired_state, predicted_state))

        return motor_signals
