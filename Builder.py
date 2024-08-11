import Buildings
import Tile
from aitools.StateMachine import *
from World import *
from GameEntity import *
from async_funcs.entity_consumption import consume_func_villager
from configuration.villager_configuration import WORKING_TIME_END
from configuration.world_configuration import DEBUG
from common_state.Feeding import Feeding
from common_state.Idle import Idle
from gametools.ani import Ani
from gametools.vector2 import Vector2
from Buildings import *
from random import *

import pygame


class Builder(GameEntity):
    def __init__(self, world, image):
        GameEntity.__init__(self, world=world, name="Builder", image_string="Entities/" + image,
                            consume_func=consume_func_villager)

        self.current_build = None

        self.speed = 80.0 * (1.0 / 60.0)
        self.base_speed = self.speed
        self.primary_state = "Waiting"
        self.hunger_limit = 60

        # Building speed of Builders
        # self.tp = 0.05

        self.building_state = Builder_Building(self)
        self.idle_state = Idle(self)
        self.Finding_state = Builder_Finding(self)
        self.feeding_state = Feeding(self)
        self.waiting_state = Waiting(self)

        self.brain.add_state(self.building_state)
        self.brain.add_state(self.idle_state)
        self.brain.add_state(self.Finding_state)
        self.brain.add_state(self.feeding_state)
        self.brain.add_state(self.waiting_state)

        self.target = None
        self.working_building = None

        self.wait_location = copy.deepcopy(self.world.get_food_court(self))
        self.animation = Ani(5, 10)
        self.pic = pygame.image.load("Images/Entities/map.png")
        self.img_func = ImageFuncs(18, 17, self.pic)
        self.sprites = self.img_func.get_images(5, 0, 4)
        self.hit = 0
        self.update()

    def update(self):
        # Updates image every 10 cycles and adds 1 to the hit count; tilling and harvesting require 4 hits;
        # sowing and watering require 8 hits
        self.image = self.sprites[self.animation.get_frame()]
        self.image.set_colorkey((255, 0, 255))
        if self.animation.finished:
            # print("Farmer id " + str(self.id) + " hit +1.")
            # self.hit += 1
            self.animation.finished = False


class Builder_Building(State):
    def __init__(self, Builder):
        State.__init__(self, "Building")
        self.Builder = Builder

    def check_conditions(self):
        self.Builder.update()

        if self.Builder.location.get_distance_to(self.Builder.destination) < 2:
            self.Builder.location = self.Builder.destination

        if self.Builder.working_building.time_to_build <= 0:
            self.Builder.world.building_list.pop(0)
            for y in range(self.Builder.working_building.SIZE_Y):
                for x in range(self.Builder.working_building.SIZE_X):
                    if DEBUG:
                        print("New building location: " + str(self.Builder.working_building.location) + ", Builder ID "
                              + str(self.Builder.id) + "'s destination is " + str(self.Builder.destination))
                    new_bldg_tile_x = self.Builder.working_building.location.x + x
                    new_bldg_tile_y = self.Builder.working_building.location.y + y
                    new_bldg_tile = Tile.BuildingTile(self.Builder.world, "Cobble")
                    new_bldg_tile.location = vector2.Vector2(new_bldg_tile_x, new_bldg_tile_y) * 32
                    new_bldg_tile.rect.topleft = new_bldg_tile.location
                    self.Builder.world.tile_array[int(new_bldg_tile_y)][int(new_bldg_tile_x)] = new_bldg_tile
                    self.Builder.world.world_surface.blit(new_bldg_tile.img, new_bldg_tile.location)

            self.Builder.working_building.image = self.Builder.working_building.finish_image
            self.Builder.working_building.unfinished_image = None
            self.Builder.working_building = None
            self.Builder.target = None
            self.Builder.destination = self.Builder.wait_location
            # self.Builder.world.BuildingQueue.remove(self.Builder.target)
            return self.Builder.primary_state

        if self.Builder.food < self.Builder.hunger_limit:
            return "Feeding"
        if self.Builder.world.time >= WORKING_TIME_END:
            return "Idle"

    def do_actions(self):
        self.Builder.working_building.time_to_build -= self.Builder.tp

    def entry_actions(self):
        # self.Builder.destination = self.Builder.location.copy()
        # self.building_complete = 0.0
        if self.Builder.working_building is None:
            new_bldg = self.Builder.target["class"](
                self.Builder.world, copy.deepcopy(self.Builder.target["location"]))
            if DEBUG:
                print("World limit check. MAXWood:" + str(self.Builder.world.MAXWood) + ", MAXStone: " + str(
                    self.Builder.world.MAXStone) + ", MAXCrop: " + str(
                    self.Builder.world.MAXCrop) + ", MAXFish: " + str(
                    self.Builder.world.MAXFish) + ", MAXpopulation: " + str(self.Builder.world.MAXpopulation))
            match (self.Builder.target["class"].SIZE_X, self.Builder.target["class"].SIZE_Y):
                case (2, 2):
                    new_bldg.image = new_bldg.unfinished_image
                case (1, 1):
                    pass
                    # new_bldg.image = Buildings.UnderConstruction1x1
            self.Builder.world.add_building(new_bldg)
            self.Builder.working_building = new_bldg


class Builder_Finding(State):  # Finding a suitable place to build.
    """If:
    Lumberyard - In the woods not near anything else
    Docks - Edge of the water, decently distanced from others
    House - Somewhere in the town area
    Manor - near top of the map or maybe replaces a house.
    """

    def __init__(self, Builder):
        State.__init__(self, "Finding")
        self.Builder = Builder

    def check_conditions(self):
        if self.Builder.target is None:
            return "Waiting"

        if self.Builder.location.get_distance_to(self.Builder.destination) < 2:
            self.Builder.location = self.Builder.destination
            return "Building"

        if self.Builder.food < self.Builder.hunger_limit:
            return "Feeding"
        if self.Builder.world.time >= WORKING_TIME_END:
            return "Idle"

    def do_actions(self):
        pass

    def entry_actions(self):
        try:
            self.Builder.target = None
            self.Builder.target = self.Builder.world.building_list[0]
            if self.Builder.target is None:
                return
            if (self.Builder.world.wood >= self.Builder.target["class"].COST_WOOD and
                    self.Builder.world.stone >= self.Builder.target["class"].COST_STONE):
                if DEBUG:
                    print("New building requires wood: " + str(self.Builder.target["class"].COST_WOOD)
                          + ", requires stone: " + str(self.Builder.target["class"].COST_STONE)
                          + ". The village has wood: " + str(self.Builder.world.wood)
                          + ", stone: " + str(self.Builder.world.stone) + ".")
                self.Builder.world.wood -= self.Builder.target["class"].COST_WOOD
                self.Builder.world.stone -= self.Builder.target["class"].COST_STONE
                self.Builder.destination = copy.deepcopy(self.Builder.target["location"]) * 32 + Vector2(32, 32)
                self.Builder.building_class = self.Builder.target["class"]

                for y in range(self.Builder.target["class"].SIZE_Y):
                    for x in range(self.Builder.target["class"].SIZE_X):
                        if DEBUG:
                            print("New building location: " + str(self.Builder.target["location"]) + ", Builder ID "
                                  + str(self.Builder.id) + "'s destination is " + str(self.Builder.destination))
                        new_bldg_tile_x = self.Builder.target["location"].x + x
                        new_bldg_tile_y = self.Builder.target["location"].y + y
                        new_bldg_tile = Tile.BuildingTile(self.Builder.world, "Cobble")
                        new_bldg_tile.location = vector2.Vector2(new_bldg_tile_x, new_bldg_tile_y) * 32
                        new_bldg_tile.rect.topleft = new_bldg_tile.location
                        self.Builder.world.tile_array[int(new_bldg_tile_y)][int(new_bldg_tile_x)] = new_bldg_tile
                        self.Builder.world.world_surface.blit(new_bldg_tile.img, new_bldg_tile.location)

            else:
                # Building request that does not have enough resources should be given up.
                # self.Builder.world.building_list.append(self.Builder.target)
                self.Builder.target = None

        except IndexError:
            pass


class Waiting(State):
    def __init__(self, Builder):
        State.__init__(self, "Waiting")
        self.Builder = Builder

    def entry_actions(self):
        if DEBUG:
            print("Builder ID: " + str(self.Builder.id) + " entering waiting state.")
        self.Builder.destination = self.Builder.wait_location
        pass

    def check_conditions(self):
        if self.Builder.location.get_distance_to(self.Builder.destination) < 2:
            self.Builder.location = self.Builder.destination

        if len(self.Builder.world.building_list) >= 1 and self.Builder.working_building is None:
            print("Builder ID: " + str(self.Builder.id) + " noticed " + str(len(self.Builder.world.building_list))
                  + " incoming building request(s).")
            return "Finding"

        elif self.Builder.working_building is not None:
            self.Builder.destination = self.Builder.working_building.location * 32 + Vector2(32, 32)
            return "Building"

        if self.Builder.food < self.Builder.hunger_limit:
            return "Feeding"
        if self.Builder.world.time >= WORKING_TIME_END:
            return "Idle"
