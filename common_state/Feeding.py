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
        State.__init__(self, "Feeding")
        self.entity = entity

    def entry_actions(self):
        print("Feeding: " + str(self.entity.id) + ".")
        self.entity.destination = self.entity.world.get_food_court(self.entity)

    def do_actions(self):
        pass

    def check_conditions(self):
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

            if self.entity.world.time >= WORKING_TIME_END:
                return "Idle"
            else:
                return self.entity.primary_state

    def exit_actions(self):
        pass
