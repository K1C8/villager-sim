"""This class is going to be tasked with planting and harvesting crops. This
   class used to plant trees, however this has been moved to Arborist (which
   is the name of someone who takes care of trees you pleb)."""

import aitools.StateMachine
from Entities import *
from GameEntity import *
from common_state.Feeding import Feeding
from async_funcs.entity_consumption import consume_func_villager
from configuration.world_configuration import TILES_PER_FARMER
from gametools.vector2 import Vector2
from gametools.ImageFuncs import *
from gametools.ani import *
import math
import pygame
import random
import TileFuncs
import BaseFunctions

HUNGER_LIMIT = 40


class Farmer(GameEntity):
    """The main class for Farmer. See above for the description"""

    def __init__(self, world, image_string):
        """Basic initialization"""

        # Initializing the class
        GameEntity.__init__(self, world, "Farmer", "Entities/"+image_string, consume_func=consume_func_villager)

        # Creating the states
        tilling_state = FarmerTilling(self)
        feeding_state = Feeding(self)
        searching_state = FarmerSearching(self)
        sowing_state = FarmerSowing(self)

        # Adding states to the brain
        self.brain.add_state(tilling_state)
        self.brain.add_state(feeding_state)
        self.brain.add_state(searching_state)
        self.brain.add_state(sowing_state)

        self.max_speed = 80.0 * (1.0 / 60.0)
        self.view_range = 1
        self.speed = self.max_speed
        self.base_speed = self.speed

        self.worldSize = world.world_size
        self.TileSize = self.world.tile_size
        self.primary_state = "Searching"

        # animation variables
        self.animation = Ani(6, 10)
        self.pic = pygame.image.load("Images/Entities/map.png")
        self.img_func = ImageFuncs(18, 17, self.pic)
        self.sprites = self.img_func.get_images(6, 0, 3)
        self.hit = 0
        self.update()

    def update(self):
        # Updates image every 10 cycles and adds 1 to the 4 hit dig
        self.image = self.sprites[self.animation.get_frame()]
        self.image.set_colorkey((255, 0, 255))
        if self.animation.finished:
            self.hit += 1
            self.animation.finished = False


class FarmerTilling(aitools.StateMachine.State):
    """
    This state will be used to have the Farmer tiling.
    """

    def __init__(self, farmer):
        aitools.StateMachine.State.__init__(self, "Tilling")
        self.farmer = farmer

    def entry_actions(self):
        BaseFunctions.random_dest(self.farmer)

    def do_actions(self):
        pass

    def check_conditions(self):
        # If there is no more room to add another tile to farm, return to searching
        if self.farmer.world.farmer_count * TILES_PER_FARMER <= len(self.farmer.world.fields):
            return self.farmer.primary_state    # "Searching"

        check = TileFuncs.get_tile(self.farmer.world, Vector2(self.farmer.location))
        if self.farmer.location.get_distance_to(self.farmer.destination) < 15 and check.tillable:
            self.farmer.destination = Vector2(self.farmer.location)

            if check.name != "MinecraftGrass":
                self.farmer.hit = 0
                self.farmer.update()
                return "Searching"

            self.farmer.update()

            if self.farmer.hit >= 4:
                self.farmer.update()
                darkness = pygame.Surface((self.farmer.TileSize, self.farmer.TileSize))
                darkness.set_alpha(check.darkness)

                new_tile = Tile.SoilTile(self.farmer.world, "Soil2")
                new_tile.darkness = darkness

                new_tile.location = check.location
                new_tile.rect.topleft = new_tile.location
                # new_tile.color = check.color # TODO: Figure out what this does.

                self.farmer.world.tile_array[int(new_tile.location.y / 32)][int(new_tile.location.x / 32)] = new_tile
                self.farmer.world.world_surface.blit(new_tile.img, new_tile.location)
                self.farmer.world.world_surface.blit(darkness, new_tile.location)
                self.farmer.world.fields.append(new_tile)

                # TODO: Update the minimap

                self.farmer.hit = 0

                return "Searching"

        elif self.farmer.location.get_distance_to(self.farmer.destination) < self.farmer.speed:
            BaseFunctions.random_dest(self.farmer)

        # If the entity is hungry, go back to the village and feed themselves
        if self.farmer.food < HUNGER_LIMIT:
            return "Feeding"

    def exit_actions(self):
        pass


class FarmerSearching(aitools.StateMachine.State):
    """
    This state will be used to have the Farmer looking for
    tile to tile, It needs to be fast enough to have AT LEAST 20 Farmers
    with little to no framerate loss.

    Perhaps it could be used to find a clump of open grass. and then the Lumberjack
    wouldn't just wander around aimlessly searching for trees even though it
    saw some when it was just at another tree
    """

    def __init__(self, farmer):
        aitools.StateMachine.State.__init__(self, "Searching")
        self.farmer = farmer

    def entry_actions(self):
        BaseFunctions.random_dest(self.farmer)

    def do_actions(self):
        pass

    def check_conditions(self):
        if self.farmer.location.get_distance_to(self.farmer.destination) < 15:
            location_array = TileFuncs.get_vnn_array(self.farmer.world, self.farmer.location, self.farmer.view_range)

            for location in location_array:
                test_tile = TileFuncs.get_tile(self.farmer.world, location)
                if test_tile.name == "MinecraftGrass":
                    self.farmer.Tree_tile = test_tile
                    self.farmer.tree_id = test_tile.id

                    self.farmer.destination = location.copy()
                    return "Tilling"

            BaseFunctions.random_dest(self.farmer)

        if self.farmer.food < HUNGER_LIMIT:
            return "Feeding"

    def exit_actions(self):
        pass


class FarmerSowing(aitools.StateMachine.State):

    def __init__(self, farmer):
        aitools.StateMachine.State.__init__(self, "Sowing")
        self.farmer = farmer

    def entry_actions(self):
        # BaseFunctions.random_dest(self.farmer)
        pass

    def do_actions(self):
        pass

    def check_conditions(self):
        if self.farmer.food < HUNGER_LIMIT:
            return "Feeding"

    def exit_actions(self):
        pass
