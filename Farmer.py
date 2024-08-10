"""This class is going to be tasked with planting and harvesting crops. This
   class used to plant trees, however this has been moved to Arborist (which
   is the name of someone who takes care of trees you pleb)."""

import aitools.StateMachine
from Entities import *
from GameEntity import *
from common_state.Feeding import Feeding
from async_funcs.entity_consumption import consume_func_villager
from common_state.Idle import Idle
from configuration.villager_configuration import WORKING_TIME_END
from configuration.world_configuration import TILES_PER_FARMER
from gametools.vector2 import Vector2
from gametools.ImageFuncs import *
from gametools.ani import *
import math
import pygame
import random
import TileFuncs
import BaseFunctions


class Farmer(GameEntity):
    """The main class for Farmer. See above for the description"""

    def __init__(self, world, image_string):
        """Basic initialization"""

        # Initializing the class
        GameEntity.__init__(self, world, "Farmer", "Entities/" + image_string, consume_func=consume_func_villager)

        # Creating the states
        tilling_state = FarmerTilling(self)
        feeding_state = Feeding(self)
        searching_state = FarmerSearching(self)
        sowing_state = FarmerSowing(self)
        watering_state = FarmerWatering(self)
        harvesting_state = FarmerHarvesting(self)
        delivering_state = Delivering(self)
        idle_state = Idle(self)

        # Adding states to the brain
        self.brain.add_state(tilling_state)
        self.brain.add_state(feeding_state)
        self.brain.add_state(searching_state)
        self.brain.add_state(sowing_state)
        self.brain.add_state(watering_state)
        self.brain.add_state(harvesting_state)
        self.brain.add_state(delivering_state)
        self.brain.add_state(idle_state)

        self.max_speed = 80.0 * (1.0 / 60.0)
        self.view_range = 2
        self.crop = 0
        self.speed = self.max_speed
        self.base_speed = self.speed
        self.hunger_limit = 40

        self.tilling_hits = 2
        self.harvesting_hits = 2
        self.sowing_hits = 2
        self.watering_hits = 2

        self.sow_list = []
        self.water_list = []
        self.harvest_list = []

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
        # Updates image every 10 cycles and adds 1 to the hit count; tilling and harvesting require 4 hits;
        # sowing and watering require 8 hits
        self.image = self.sprites[self.animation.get_frame()]
        self.image.set_colorkey((255, 0, 255))
        if self.animation.finished:
            # print("Farmer id " + str(self.id) + " hit +1.")
            self.hit += 1
            self.animation.finished = False


class FarmerTilling(aitools.StateMachine.State):
    """
    This state will be used to have the Farmer tiling.
    """

    def __init__(self, farmer: Farmer):
        aitools.StateMachine.State.__init__(self, "Tilling")
        self.farmer = farmer

    def entry_actions(self):
        # BaseFunctions.random_dest(self.farmer)
        pass

    def do_actions(self):
        pass

    def check_conditions(self):
        # If there is no more room to add another tile to farm, return to searching
        if self.farmer.world.farmer_count * TILES_PER_FARMER <= len(self.farmer.world.fields):
            return self.farmer.primary_state  # "Searching"

        check = TileFuncs.get_tile(self.farmer.world, Vector2(self.farmer.location))
        if (self.farmer.location.get_distance_to(self.farmer.destination) < (0.5 * self.farmer.world.tile_size)
                and check.tillable):
            self.farmer.destination = Vector2(self.farmer.location)

            if check.name != "MinecraftGrass":
                self.farmer.hit = 0
                self.farmer.update()
                return self.farmer.primary_state

            self.farmer.update()

            if self.farmer.hit >= self.farmer.tilling_hits:
                self.farmer.update()
                # darkness = pygame.Surface((self.farmer.TileSize, self.farmer.TileSize))
                # darkness.set_alpha(check.darkness)

                shade = pygame.Surface((self.farmer.TileSize, self.farmer.TileSize))
                shade.set_alpha(check.darkness)

                new_tile = Tile.SoilTile(self.farmer.world, "Soil2")
                # new_tile.darkness = darkness
                new_tile.darkness = check.darkness

                new_tile.location = check.location
                new_tile.rect.topleft = new_tile.location
                # new_tile.color = check.color # TODO: Figure out what this does.

                self.farmer.world.tile_array[int(new_tile.location.y / 32)][int(new_tile.location.x / 32)] = new_tile
                self.farmer.world.world_surface.blit(new_tile.img, new_tile.location)
                # self.farmer.world.world_surface.blit(darkness, new_tile.location)
                self.farmer.world.world_surface.blit(shade, new_tile.location)
                self.farmer.world.fields.append(new_tile)
                self.farmer.world.sow_queue.put(new_tile)

                # TODO: Update the minimap

                self.farmer.hit = 0

                # print("Farmer id " + str(self.farmer.id) + " has tilled a tile, finding next tile from (" +
                #       str(self.farmer.location.x / self.farmer.world.tile_size) + ", " +
                #       str(self.farmer.location.y / self.farmer.world.tile_size) + ").")

                # Find a nearby tillable tile
                nearby_array = TileFuncs.get_vnn_array(self.farmer.world, self.farmer.location, self.farmer.view_range)
                for location in nearby_array:
                    test_tile = TileFuncs.get_tile(self.farmer.world, location)
                    if test_tile.name == "MinecraftGrass":
                        self.farmer.destination = location
                        # print("Farmer id " + str(self.farmer.id) + " has found a new tile to till, next tile is (" +
                        #       str(location.x / self.farmer.world.tile_size) + ", " +
                        #       str(location.y / self.farmer.world.tile_size) + ").")
                        return

                return self.farmer.primary_state

        elif self.farmer.location.get_distance_to(self.farmer.destination) < self.farmer.speed:
            BaseFunctions.random_dest(self.farmer)

        # If the entity is hungry, go back to the village and feed themselves
        if self.farmer.food < self.farmer.hunger_limit:
            return "Feeding"
        # If the time is about to sunset, go back to the rest spot in the village
        if self.farmer.world.time >= WORKING_TIME_END:
            return "Idle"

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

    def __init__(self, farmer: Farmer):
        aitools.StateMachine.State.__init__(self, "Searching")
        self.farmer = farmer

    def entry_actions(self):
        BaseFunctions.random_dest(self.farmer)

    def do_actions(self):
        pass

    def check_conditions(self):

        if (len(self.farmer.harvest_list) > 0 or
                (self.farmer.world.harvest_queue is not None and not self.farmer.world.harvest_queue.empty())):
            if len(self.farmer.harvest_list) > 0:
                self.farmer.destination = self.farmer.harvest_list[0].location
                print("Farmer id " + str(self.farmer.id) + " harvest list: " + str(len(self.farmer.harvest_list))
                      + ", first of the harvest list is " + str(self.farmer.harvest_list[0].location))
            else:
                harvest_tile = self.farmer.world.harvest_queue.get()
                self.farmer.harvest_list.append(harvest_tile)
                self.farmer.destination = harvest_tile.location
            return "Harvesting"

        # Check if farmers can till more tiles and if the current tile can till, or find the next place to till
        elif (len(self.farmer.sow_list) == 0 and len(self.farmer.water_list) == 0
              and self.farmer.world.farmer_count * TILES_PER_FARMER > len(self.farmer.world.fields)):
            if self.farmer.location.get_distance_to(self.farmer.destination) < 15:
                location_array = TileFuncs.get_vnn_array(self.farmer.world, self.farmer.location,
                                                         self.farmer.view_range)

                for location in location_array:
                    test_tile = TileFuncs.get_tile(self.farmer.world, location)
                    if test_tile.name == "MinecraftGrass":
                        self.farmer.Tree_tile = test_tile
                        self.farmer.tree_id = test_tile.id

                        self.farmer.destination = location.copy()
                        return "Tilling"

                # If the current tile cannot till, go to the next
                BaseFunctions.random_dest(self.farmer)

        # If farmers have tilled enough tiles, then find one task to do
        # Add Sowing, Watering, and Harvesting checks here. These ops have to search in order.
        elif (len(self.farmer.sow_list) > 0 or
              (self.farmer.world.sow_queue is not None and not self.farmer.world.sow_queue.empty())):
            if len(self.farmer.sow_list) > 0:
                print("Farmer id " + str(self.farmer.id) + " sow list: " + str(len(self.farmer.sow_list))
                      + ", first of the sow list is " + str(self.farmer.sow_list[0].location))
                self.farmer.destination = self.farmer.sow_list[0].location
            else:
                sow_tile = self.farmer.world.sow_queue.get()
                self.farmer.sow_list.append(sow_tile)
                self.farmer.destination = sow_tile.location
            return "Sowing"
        elif (len(self.farmer.water_list) > 0 or
              self.farmer.world.water_queue is not None and not self.farmer.world.water_queue.empty()):
            if len(self.farmer.water_list) > 0:
                self.farmer.destination = self.farmer.water_list[0].location
                print("Farmer id " + str(self.farmer.id) + " water list: " + str(len(self.farmer.water_list))
                      + ", first of the water list is " + str(self.farmer.water_list[0].location))
            else:
                water_tile = self.farmer.world.water_queue.get()
                self.farmer.water_list.append(water_tile)
                self.farmer.destination = water_tile.location
            return "Watering"

        elif self.farmer.world.farmer_count * TILES_PER_FARMER <= len(self.farmer.world.fields):
            return "Idle"

        if self.farmer.food < self.farmer.hunger_limit:
            return "Feeding"
        if self.farmer.world.time >= WORKING_TIME_END:
            return "Idle"

    def exit_actions(self):
        pass


class FarmerSowing(aitools.StateMachine.State):

    def __init__(self, farmer: Farmer):
        aitools.StateMachine.State.__init__(self, "Sowing")
        self.farmer = farmer

    def entry_actions(self):
        # BaseFunctions.random_dest(self.farmer)
        pass

    def do_actions(self):
        pass

    def check_conditions(self):
        check = TileFuncs.get_tile(self.farmer.world, Vector2(self.farmer.location))
        if (self.farmer.location.get_distance_to(self.farmer.destination) < (0.10 * self.farmer.world.tile_size)
                and check.crop_plantable):
            # This will snap the farmer to the target tile.
            self.farmer.location = Vector2(self.farmer.destination)
            check = TileFuncs.get_tile(self.farmer.world, Vector2(self.farmer.location))

            # Extra caution measurement for the imprecise entity movement
            if check.name != "Soil2":
                print("Farmer id " + str(self.farmer.id) + " on wrong tile.")
                self.farmer.hit = 0
                self.farmer.update()
                return self.farmer.primary_state

            # print("Farmer id " + str(self.farmer.id) + " on correct tile.")
            self.farmer.update()

            if self.farmer.hit >= self.farmer.sowing_hits:
                self.farmer.update()
                # darkness = pygame.Surface((self.farmer.TileSize, self.farmer.TileSize))
                # darkness.set_alpha(check.darkness)

                shade = pygame.Surface((self.farmer.TileSize, self.farmer.TileSize))
                shade.set_alpha(check.darkness)

                new_tile = Tile.ShootFieldTile(self.farmer.world, "ShootField")
                # new_tile.darkness = darkness
                new_tile.darkness = check.darkness

                new_tile.location = check.location
                new_tile.rect.topleft = new_tile.location
                # new_tile.color = check.color # TODO: Figure out what this does.

                self.farmer.world.tile_array[int(new_tile.location.y / 32)][int(new_tile.location.x / 32)] = new_tile
                self.farmer.world.world_surface.blit(new_tile.img, new_tile.location)
                self.farmer.world.world_surface.blit(shade, new_tile.location)
                # self.farmer.world.fields.append(new_tile)
                self.farmer.world.water_queue.put(new_tile)
                self.farmer.sow_list.remove(check)

                # TODO: Update the minimap
                self.farmer.hit = 0

                return self.farmer.primary_state

        # else:
        #     return self.farmer.primary_state

        if self.farmer.food < self.farmer.hunger_limit:
            return "Feeding"
        if self.farmer.world.time >= WORKING_TIME_END:
            return "Idle"

    def exit_actions(self):
        pass


class FarmerWatering(aitools.StateMachine.State):

    def __init__(self, farmer: Farmer):
        aitools.StateMachine.State.__init__(self, "Watering")
        self.farmer = farmer

    def entry_actions(self):
        # BaseFunctions.random_dest(self.farmer)
        pass

    def do_actions(self):
        pass

    def check_conditions(self):
        check = TileFuncs.get_tile(self.farmer.world, Vector2(self.farmer.location))
        if (self.farmer.location.get_distance_to(self.farmer.destination) < (0.10 * self.farmer.world.tile_size)
                and check.crop_waterable):
            # This will snap the farmer to the target tile.
            self.farmer.location = Vector2(self.farmer.destination)
            check = TileFuncs.get_tile(self.farmer.world, Vector2(self.farmer.location))

            # Extra caution measurement for the imprecise entity movement
            if check.name != "ShootField":
                print("Farmer id " + str(self.farmer.id) + " on wrong tile.")
                self.farmer.hit = 0
                self.farmer.update()
                return self.farmer.primary_state

            # print("Farmer id " + str(self.farmer.id) + " on correct tile.")
            self.farmer.update()

            if self.farmer.hit >= self.farmer.watering_hits:
                self.farmer.update()
                # Check if the tile is watered enough to mature
                if check.watered_times >= check.watered_req:
                    shade = pygame.Surface((self.farmer.TileSize, self.farmer.TileSize))
                    shade.set_alpha(check.darkness)

                    new_tile = Tile.MatureFieldTile(self.farmer.world, "MatureField")
                    # new_tile.darkness = darkness
                    new_tile.darkness = check.darkness

                    new_tile.location = check.location
                    new_tile.rect.topleft = new_tile.location
                    # new_tile.color = check.color # TODO: Figure out what this does.

                    self.farmer.world.tile_array[int(new_tile.location.y / 32)][
                        int(new_tile.location.x / 32)] = new_tile
                    self.farmer.world.world_surface.blit(new_tile.img, new_tile.location)
                    self.farmer.world.world_surface.blit(shade, new_tile.location)
                    # self.farmer.world.fields.append(new_tile)
                    self.farmer.world.harvest_queue.put(new_tile)
                    self.farmer.water_list.remove(check)
                else:
                    check.watered_times += 1
                    self.farmer.world.water_queue.put(check)
                    self.farmer.water_list.remove(check)

                # TODO: Update the minimap
                self.farmer.hit = 0

                return self.farmer.primary_state

        if self.farmer.food < self.farmer.hunger_limit:
            return "Feeding"
        if self.farmer.world.time >= WORKING_TIME_END:
            return "Idle"

    def exit_actions(self):
        pass


class FarmerHarvesting(aitools.StateMachine.State):

    def __init__(self, farmer: Farmer):
        aitools.StateMachine.State.__init__(self, "Harvesting")
        self.farmer = farmer

    def entry_actions(self):
        # BaseFunctions.random_dest(self.farmer)
        pass

    def do_actions(self):
        pass

    def check_conditions(self):
        check = TileFuncs.get_tile(self.farmer.world, Vector2(self.farmer.location))
        if (self.farmer.location.get_distance_to(self.farmer.destination) < (0.5 * self.farmer.world.tile_size)
                and check.crop_harvestable):
            self.farmer.destination = Vector2(self.farmer.location)

            if check.name != "MatureField":
                self.farmer.hit = 0
                self.farmer.update()
                return self.farmer.primary_state

            self.farmer.update()

            if self.farmer.hit >= self.farmer.harvesting_hits:
                self.farmer.update()
                # darkness = pygame.Surface((self.farmer.TileSize, self.farmer.TileSize))
                # darkness.set_alpha(check.darkness)

                shade = pygame.Surface((self.farmer.TileSize, self.farmer.TileSize))
                shade.set_alpha(check.darkness)

                new_tile = Tile.SoilTile(self.farmer.world, "Soil2")
                # new_tile.darkness = darkness
                new_tile.darkness = check.darkness

                new_tile.location = check.location
                new_tile.rect.topleft = new_tile.location
                # new_tile.color = check.color # TODO: Figure out what this does.

                self.farmer.world.tile_array[int(new_tile.location.y / 32)][int(new_tile.location.x / 32)] = new_tile
                self.farmer.world.world_surface.blit(new_tile.img, new_tile.location)
                # self.farmer.world.world_surface.blit(darkness, new_tile.location)
                self.farmer.world.world_surface.blit(shade, new_tile.location)
                self.farmer.world.sow_queue.put(new_tile)
                self.farmer.harvest_list.remove(check)
                print("Farmer id " + str(self.farmer.id) + " have " + str(len(self.farmer.harvest_list)) +
                      " tiles to harvest.")
                # TODO: Update the minimap

                self.farmer.hit = 0
                self.farmer.crop += randint(40, 60)

                return "Delivering"

        elif self.farmer.location.get_distance_to(self.farmer.destination) < self.farmer.speed:
            BaseFunctions.random_dest(self.farmer)

        # If the entity is hungry, go back to the village and feed themselves
        if self.farmer.food < self.farmer.hunger_limit:
            return "Feeding"
        # If the time is about to sunset, go back to the rest spot in the village
        if self.farmer.world.time >= WORKING_TIME_END:
            return "Idle"

    def exit_actions(self):
        pass


class Delivering(State):

    def __init__(self, farmer):
        State.__init__(self, "Delivering")
        self.farmer = farmer

    def entry_actions(self):
        self.farmer.destination = self.farmer.world.get_barn(self.farmer)

    def do_actions(self):
        pass

    def check_conditions(self):
        if self.farmer.location.get_distance_to(self.farmer.destination) < 15:
            self.farmer.world.crop += self.farmer.crop
            self.farmer.crop = 0
            return "Feeding"

    def exit_actions(self):
        pass
