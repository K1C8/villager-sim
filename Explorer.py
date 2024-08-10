"""The explorer is a villager driven to the find the amazing by thier
unwaivering curiosity for what is unknown. These will seek new land
and features to help advance the civilization, though may at times
pursure knowledge at other costs.

Also this class was primarily developed to track down movement bugs."""

import aitools.StateMachine
from async_funcs.entity_consumption import consume_func_villager
import GameEntity
import BaseFunctions
from common_state.Feeding import Feeding
from common_state.Idle import Idle
from configuration.villager_configuration import WORKING_TIME_END


class Explorer(GameEntity.GameEntity):
    """See file doctring for the description."""


    def __init__(self, world, image_string):
        """Basic initialization for the class."""

        GameEntity.GameEntity.__init__(self, world, "Explorer", "Entities/"+image_string,
                                       consume_func=consume_func_villager)

        self.speed = 80.0 * (1.0 / 60.0)
        self.base_speed = self.speed
        self.view_range = 8
        self.hunger_limit = 50

        self.exploring_state = Exploring(self)
        self.feeding_state = Feeding(self)
        self.idle_state = Idle(self)

        self.brain.add_state(self.exploring_state)
        self.brain.add_state(self.feeding_state)
        self.brain.add_state(self.idle_state)

        self.worldSize = world.world_size
        self.TileSize = self.world.tile_size
        self.primary_state = "Exploring"

class Exploring(aitools.StateMachine.State):
    """The primary function of the explorer, to search for places previously
    unvisited or unfound. Eventually the explorer should keep track of
    and prioritize places it hasn't visited."""

    def __init__(self, this_explorer):
        aitools.StateMachine.State.__init__(self, "Exploring")
        self.explorer = this_explorer

    def entry_actions(self):
        """When the explorer starts exploring (enters exploring state)."""
        BaseFunctions.random_dest(self.explorer)

    def do_actions(self):
        """What should the explorer do while it is exploring"""
        pass

    def check_conditions(self):
        """Check if the explorer should still be exploring"""
        if self.explorer.location.get_distance_to(self.explorer.destination) <= self.explorer.speed:
            BaseFunctions.random_dest(self.explorer)

        if self.explorer.food < self.explorer.hunger_limit:
            return "Feeding"
        if self.explorer.world.time >= WORKING_TIME_END:
            return "Idle"

    def exit_actions(self):
        """What the explorer does as it stops exploring"""
        pass
