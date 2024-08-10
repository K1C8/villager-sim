from GameEntity import GameEntity
from aitools.StateMachine import State
from configuration.villager_configuration import WORKING_TIME_START, WORKING_TIME_END
from BaseFunctions import get_idle_destination


class Idle(State):
    """
        This state is to be used in every village class for resting themselves when they need to rest.
    """

    def __init__(self, entity):
        State.__init__(self, "Idle")
        self.entity = entity
        self.rested = False

    def entry_actions(self):
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
        if self.entity.location.get_distance_to(self.entity.destination) < self.entity.speed:
            self.rested = True
        if self.rested and WORKING_TIME_START <= self.entity.world.time < WORKING_TIME_END:
            if self.entity.food <= self.entity.hunger_limit:
                return "Feeding"
            else:
                return self.entity.primary_state

    def exit_actions(self):
        pass
