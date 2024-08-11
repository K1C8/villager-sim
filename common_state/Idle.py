"""
CS5150 Game AI Final Project
Team Member: Jianyan Chen, Ruidi Huang, Xin Qi
Aug 2024

This program defines the `Idle` state for villagers in the game.
"""
from GameEntity import GameEntity
from aitools.StateMachine import State
from configuration.villager_configuration import WORKING_TIME_START, WORKING_TIME_END
from BaseFunctions import get_idle_destination


class Idle(State):
    """
    This state is to be used in every village class for resting themselves when they need to rest.
    """

    def __init__(self, entity):
        """
        Initializes the Idle state with the given entity (villager).

        Args:
            entity (GameEntity): The villager entity that will be in the Idle state.
        """
        State.__init__(self, "Idle")
        self.entity = entity
        self.rested = False

    def entry_actions(self):
        """
        Actions to perform upon entering the Idle state.
        This method sets the villager's destination to a designated resting location.

        If a valid destination is found, the villager moves towards it.
        """
        self.rested = False
        # print("Entity id " + str(self.entity.id) + " has entered idle state.")
        # self.Builder.destination = self.Builder.IdleLocation
        destination = get_idle_destination(self.entity)
        if destination is not None:
            # print("Entity id " + str(self.entity.id) + " is going to rest.")
            self.entity.destination = destination

    def do_actions(self):
        pass

    def check_conditions(self):
        """
        Checks the conditions to determine whether the villager should remain in the Idle state
        or transition to another state.

        If the villager has reached their resting location and it is within the working hours,
        they may transition to the Feeding state if hungry or return to their primary state.

        Returns:
            str: The name of the next state if a transition should occur, or None to stay in the Idle state.
        """
        # Check if the villager has reached the resting destination
        if self.entity.location.get_distance_to(self.entity.destination) < self.entity.speed:
            self.rested = True
            # Once rested, set the destination to the current location (to stop moving)
            self.entity.destination = self.entity.location
         # If the villager has rested and it's daytime, transition to the appropriate state
        if self.rested and WORKING_TIME_START <= self.entity.world.time < WORKING_TIME_END:
            if self.entity.food <= self.entity.hunger_limit:
                return "Feeding"
            else:
                return self.entity.primary_state

    def exit_actions(self):
        pass
