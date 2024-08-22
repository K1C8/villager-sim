"""
CS5150 Game AI Final Project
Team Member: Jianyan Chen, Ruidi Huang, Xin Qi
Aug 2024

This program defines the Explorer class for villagers in the game.
Explorers find stone in the world and takes them back home.
"""


import random
import aitools.StateMachine
from async_funcs.entity_consumption import consume_func_villager
import GameEntity
import BaseFunctions
from common_state.Feeding import Feeding
from common_state.Idle import Idle
from configuration.villager_configuration import WORKING_TIME_END
from gametools.vector2 import *
import Tile
import TileFuncs

class Explorer(GameEntity.GameEntity):
    """The Explorer class is responsible for searching and collecting resources (specifically stone)
    within the game world, while managing its state transitions between different actions like exploring, 
    collecting, and feeding."""
 
    def __init__(self, world, image_string):
        """Initializes the Explorer object with its attributes and states.

        Args:
            world (World): The game world instance.
            image_string (str): The string to load the Explorer's image.
        """

        GameEntity.GameEntity.__init__(self, world, "Explorer", "Entities/"+image_string,
                                       consume_func=consume_func_villager)

        self.speed = 80.0 * (1.0 / 60.0)
        self.base_speed = self.speed
        self.view_range = 8
        self.hunger_limit = 50

        self.exploring_state = Exploring(self)
        self.feeding_state = Feeding(self)
        self.idle_state = Idle(self)
        self.search_stone_state = SearchStone(self)
        self.collect_stone_state = CollectStone(self)
        self.return_state = Return(self)
        self.unload_stone_state = UnloadStone(self)

        self.brain.add_state(self.exploring_state)
        self.brain.add_state(self.feeding_state)
        self.brain.add_state(self.idle_state)
        self.brain.add_state(self.search_stone_state)
        self.brain.add_state(self.collect_stone_state)
        self.brain.add_state(self.return_state)
        self.brain.add_state(self.unload_stone_state)

        self.worldSize = world.world_size
        self.TileSize = self.world.tile_size
        self.primary_state = "SearchStone"
        
        self.stone = 0
        self.MAX_STONE = 50
        self.collect_speed = 0.5
        self.unload_speed = 1

class SearchStone(aitools.StateMachine.State):
    """State where the Explorer searches for stone resources within the game world."""
    def __init__(self, this_explorer):
        """Initializes the SearchStone state.

        Args:
            this_explorer (Explorer): The Explorer object in this state.
        """
        aitools.StateMachine.State.__init__(self, "SearchStone")
        self.explorer = this_explorer
        
    def entry_actions(self):
        """When the explorer starts exploring (enters exploring state)."""
        BaseFunctions.random_dest(self.explorer)
        

    def do_actions(self):
        """Actions performed by the Explorer while in the SearchStone state."""
        curr_tile = self.explorer.world.tile_array[self.explorer.tile_location_y][self.explorer.tile_location_x] 
        if self.explorer.location == self.explorer.destination:
            BaseFunctions.random_dest(self.explorer)      
        pass
    
    def check_conditions(self):
        """Checks whether conditions are met to transition out of the SearchStone state.

        Returns:
            str: The name of the next state to transition to, if any.
        """
        
        curr_tile = self.explorer.world.tile_array[self.explorer.tile_location_y][self.explorer.tile_location_x] 

        # Transition to CollectStone if a stone tile is found
        if isinstance(curr_tile, Tile.SmoothStoneTile) \
        or isinstance(curr_tile, Tile.CobblestoneTile): 
            return "CollectStone" 
        
        curr_tile = self.explorer.world.tile_array[self.explorer.tile_location_y][self.explorer.tile_location_x]

        # Continue moving to a new destination
        if self.explorer.location.get_distance_to(self.explorer.destination) < (0.5 * self.explorer.world.tile_size):
            # if self.explorer.location == self.explorer.destination:
            BaseFunctions.random_dest(self.explorer)

        # Check for transitions to Feeding or Idle states
        if self.explorer.food < self.explorer.hunger_limit:
            return "Feeding"
        if self.explorer.world.time >= WORKING_TIME_END:
            return "Idle"
            
    def exit_actions(self):
        """What the explorer does as it stops exploring"""
        self.explorer.destination = self.explorer.location
        pass
       
class CollectStone(aitools.StateMachine.State):
    """State where the Explorer collects stone resources from a stone tile."""

    def __init__(self, this_explorer):
        """Initializes the CollectStone state.

        Args:
            this_explorer (Explorer): The Explorer object in this state.
        """
        aitools.StateMachine.State.__init__(self, "CollectStone")
        self.explorer = this_explorer

    def entry_actions(self):
        """When the explorer starts collecting stone (enters collecting stone state)."""
        # BaseFunctions.random_dest(self.explorer)
        pass

    def do_actions(self):
        """What should the explorer do while it is collecting stone"""
        if self.explorer.stone < self.explorer.MAX_STONE:
            self.explorer.stone += self.explorer.collect_speed

    def check_conditions(self):
        """Check if the explorer should still be collecting stone"""
        if self.explorer.stone >= self.explorer.MAX_STONE:
            return "Return"

    def exit_actions(self):
        """What the explorer does as it stops collecting stone"""
        self.explorer.destination = self.explorer.world.get_stonework(self.explorer) 
        
class Return(aitools.StateMachine.State):
    """State where the Explorer returns to the base or drop-off point after collecting stone."""

    def __init__(self, this_explorer):
        """Initializes the Return state.

        Args:
            this_explorer (Explorer): The Explorer object in this state.
        """
        aitools.StateMachine.State.__init__(self, "Return")
        self.explorer = this_explorer

    def entry_actions(self):
        """Actions taken when the Explorer enters the Return state."""
        pass
    
    def do_actions(self):
        """Actions performed by the Explorer while returning to the base."""
        pass

    def check_conditions(self):
        """Checks whether conditions are met to transition out of the Return state.

        Returns:
            str: The name of the next state to transition to, if any.
        """
        curr_tile = TileFuncs.get_tile(self.explorer.world, self.explorer.location)
        dest_tile = TileFuncs.get_tile(self.explorer.world, self.explorer.destination)
        if curr_tile == dest_tile:
            return "UnloadStone"
        
    def exit_actions(self):
        """Actions taken when the Explorer exits the Return state."""
        pass
    
class UnloadStone(aitools.StateMachine.State):
    """State where the Explorer unloads the collected stone at the base or drop-off point."""

    def __init__(self, this_explorer):
        """Initializes the UnloadStone state.

        Args:
            this_explorer (Explorer): The Explorer object in this state.
        """
        aitools.StateMachine.State.__init__(self, "UnloadStone")
        self.explorer = this_explorer

    def entry_actions(self):
        """Actions taken when the Explorer enters the UnloadStone state."""

    def do_actions(self):
        """Actions performed by the Explorer while unloading stone."""
        if self.explorer.stone > 0:
            self.explorer.stone -= self.explorer.unload_speed
            self.explorer.world.stone += self.explorer.unload_speed

    def check_conditions(self):
        """Checks whether conditions are met to transition out of the UnloadStone state.

        Returns:
            str: The name of the next state to transition to, if any.
        """
        if self.explorer.hunger_limit > self.explorer.food:
            return "Feeding"
        
        if self.explorer.stone <= 0:
            return "SearchStone"
        
    def exit_actions(self):
        """Actions taken when the Explorer exits the UnloadStone state."""
        BaseFunctions.random_dest(self.explorer)
        pass
    
class Exploring(aitools.StateMachine.State):
    """State where the Explorer searches for new areas or resources."""

    def __init__(self, this_explorer):
        """Initializes the Exploring state.

        Args:
            this_explorer (Explorer): The Explorer object in this state.
        """
        aitools.StateMachine.State.__init__(self, "Exploring")
        self.explorer = this_explorer

    def entry_actions(self):
        """When the explorer starts exploring (enters exploring state)."""
        BaseFunctions.random_dest(self.explorer)

    def do_actions(self):
        """What should the explorer do while it is exploring"""
        pass

    def check_conditions(self):
        """Checks whether conditions are met to transition out of the Exploring state.

        Returns:
            str: The name of the next state to transition to, if any.
        """
        if self.explorer.location.get_distance_to(self.explorer.destination) <= self.explorer.speed:
            BaseFunctions.random_dest(self.explorer)

        if self.explorer.food < self.explorer.hunger_limit:
            return "Feeding"
        if self.explorer.world.time >= WORKING_TIME_END:
            return "Idle"

    def exit_actions(self):
        """What the explorer does as it stops exploring"""
        pass
