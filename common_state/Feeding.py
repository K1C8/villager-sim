"""
CS5150 Game AI Final Project
Team Member: Jianyan Chen, Ruidi Huang, Xin Qi
Aug 2024

This program defines the `Feeding` state for villagers in the game.
"""

import copy
import BaseFunctions
import TileFuncs
from aitools.StateMachine import State
from configuration.villager_configuration import FEEDING_THRESHOLD, WORKING_TIME_END


class Feeding(State):
    """
    This state is to be used in every village class for feeding themselves when their food cound drops below their
    hunger limit.
    """

    def __init__(self, entity):
        """
        Initializes the Feeding state with the given entity (villager).

        Args:
            entity (GameEntity): The villager entity that will be in the Feeding state.
        """
        State.__init__(self, "Feeding")
        self.entity = entity

    def entry_actions(self):
        """
        Actions to perform upon entering the Feeding state.
        This sets the villager's destination to the food court in the village.
        """
        print("Feeding: " + str(self.entity.id) + " at " + str(self.entity.destination))
        self.entity.destination = copy.deepcopy(self.entity.world.get_food_court(self.entity))

    def do_actions(self):
        pass

    def check_conditions(self):
        """
        Checks the conditions to determine whether the villager should remain in the Feeding state
        or transition to another state.

        If the villager reaches the food court and their food level is below the threshold,
        they consume food from the village's resources. The villager then either transitions to the Idle state
        if the day has ended, or returns to their primary state.

        Returns:
            str: The name of the next state if a transition should occur, or None to stay in the Feeding state.
        """
        if self.entity.location.get_distance_to(self.entity.destination) < 15:
            # Temporary code, this logic of feeding the villagers should come after checking there is
            # enough food in the village. It is giving food for free now, but the available food display in the status
            # bar can go negative.
            if self.entity.food < FEEDING_THRESHOLD:
                self.entity.food = 100
                if self.entity.world.fish > 0:
                    self.entity.world.fish -= 1
                elif self.entity.world.crop > 0:
                    self.entity.world.crop -= 1

            # Transition to the Idle state if the day has ended
            if self.entity.world.time >= WORKING_TIME_END:
                return "Idle"
            else:
                return self.entity.primary_state  # Return to the villager's primary state

    def exit_actions(self):
        pass
