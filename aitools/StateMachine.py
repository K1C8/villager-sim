"""
CS5150 Game AI Final Project
Team Member: Jianyan Chen, Ruidi Huang, Xin Qi
Aug 2024

State and StateMachine classes for implementing a finite state machine (FSM) in AI.
These classes allow for managing states in an entity, where each state can perform actions,
check conditions for transitioning to other states, and execute entry and exit actions.
"""

class State(object):
    """
    Represents a single state in a state machine.
    This class provides the basic structure for a state, including actions to perform
    while in the state, conditions to check for transitioning out of the state,
    and actions to perform when entering or exiting the state.
    """
    def __init__(self, name):
        """
        Initializes the state with a given name.

        Args:
            name (str): The name of the state.
        """
        self.name = name

    def do_actions(self):
        """
        Defines the actions to perform while in this state.
        Intended to be overridden by subclasses with specific behavior.
        """
        pass

    def check_conditions(self):
        """
        Checks whether conditions are met to transition out of this state.
        Intended to be overridden by subclasses with specific behavior.
        """
        pass

    def entry_actions(self):
        """
        Defines actions to perform when entering this state.
        Intended to be overridden by subclasses with specific behavior.
        """
        pass

    def exit_actions(self):
        """
        Defines actions to perform when exiting this state.
        Intended to be overridden by subclasses with specific behavior.
        """
        pass


class StateMachine(object):
    """
    Manages the states for an entity, allowing it to transition between states based on conditions.
    The StateMachine keeps track of the active state and handles transitions between states.
    """
    def __init__(self):
        """
        Initializes the state machine with an empty state dictionary and no active state.
        """
        self.states = {} # Dictionary to store states by their names
        self.active_state = None # The current active state

    def add_state(self, state):
        """
        Adds a state to the state machine.

        Args:
            state (State): The state to be added to the state machine.
        """
        self.states[state.name] = state

    def think(self):
        """
        Executes the current state's actions and checks for transitions to other states.
        This method should be called regularly to update the state machine's logic.
        """
        if self.active_state is None:
            return

        # Perform actions as the current state indicates
        self.active_state.do_actions()

        # Check if conditions are met to switch to next state
        new_state_name = self.active_state.check_conditions()
        if new_state_name is not None:
            self.set_state(new_state_name)

    def set_state(self, new_state_name):
        """
        Transitions the state machine to a new state.

        Args:
            new_state_name (str): The name of the new state to transition to.
        """

        if self.active_state is not None:
            # Perform any cleanup or final actions for the current state
            self.active_state.exit_actions()

        # Set the new state as the active state and perform entry actions
        self.active_state = self.states[new_state_name]
        self.active_state.entry_actions()
