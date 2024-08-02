import BaseFunctions
import TileFuncs
from aitools.StateMachine import State


class Feeding(State):
    """
    This state is to be used in every village class for feeding themselves when their food cound drops below their
    hunger limit.
    """

    def __init__(self, entity):
        State.__init__(self, "Feeding")
        self.entity = entity

    def entry_actions(self):
        self.entity.destination = self.entity.world.get_food_court()

    def do_actions(self):
        pass

    def check_conditions(self):
        if self.entity.location.get_distance_to(self.entity.destination) < 15:
            self.entity.food = 100
            return self.entity.primary_state

    def exit_actions(self):
        pass
