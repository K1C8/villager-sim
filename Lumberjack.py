"""
CS5150 Game AI Final Project
Team Member: Jianyan Chen, Ruidi Huang, Xin Qi
Aug 2024

This program contains classes related to Lumberjack.
The Lumberjack class represents a villager whose primary task is to search for trees, chop them down,
and deliver the wood to a lumberyard.
"""

from aitools.StateMachine import *
from Entities import *
from GameEntity import *
from common_state.Feeding import Feeding
from common_state.Idle import Idle
from configuration.villager_configuration import WORKING_TIME_END
from gametools.vector2 import Vector2
from gametools.ImageFuncs import *
from gametools.ani import *
import Tile
import math
import pygame
import random
from async_funcs.entity_consumption import consume_func_villager
import TileFuncs
from World import *
import BaseFunctions

NoTreeImg = pygame.image.load("Images/Tiles/MinecraftGrass.png")


class Lumberjack(GameEntity):
    """
    The Lumberjack class represents a villager whose primary task is to search for trees, chop them down,
    and deliver the wood to a lumberyard.
    """
    def __init__(self, world, image_string):
        """
        Initializes a Lumberjack object with basic attributes such as position, speed, and states.

        Args:
            world (World): The game world the Lumberjack exists in.
            image_string (str): The path to the Lumberjack's image file.
        """
        # Initializing the class
        GameEntity.__init__(self, world, "Lumberjack", "Entities/"+image_string,
                            consume_func=consume_func_villager)

        self.speed = 100.0 * (1.0 / 60.0)
        self.base_speed = self.speed
        self.view_range = 6
        self.hunger_limit = 40

        # Creating the states
        self.searching_state = Searching(self)
        self.chopping_state = Chopping(self)
        self.delivering_state = Delivering(self)
        self.feeding_state = Feeding(self)
        self.idle_state = Idle(self)

        # Adding states to the brain
        self.brain.add_state(self.searching_state)
        self.brain.add_state(self.chopping_state)
        self.brain.add_state(self.delivering_state)
        self.brain.add_state(self.feeding_state)
        self.brain.add_state(self.idle_state)

        self.worldSize = world.world_size
        self.TileSize = self.world.tile_size
        self.primary_state = "Searching"

        # animation variables
        self.animation = Ani(5,10)
        self.pic = pygame.image.load("Images/Entities/map.png")
        self.img_func = ImageFuncs(18, 17,self.pic)
        self.sprites = self.img_func.get_images(5,0,1)
        self.hit = 0
        self.update()

    def update(self):
        """
        Updates the Lumberjack's animation frame and handles the chopping action.
        """
        # Updates image every 10 cycles and adds 1 to the 4 hit dig
        self.image = self.sprites[self.animation.get_frame()]
        self.image.set_colorkey((255,0,255))
        if self.animation.finished:
            self.hit += 1
            self.animation.finished = False


class Searching(State):
    """This state will be used to have the Lumberjack looking for
       trees to cut, It needs to be fast enough to have AT LEAST 20 Lumberjacks
       with little to no framerate loss.
       
       Perhaps it could be used to find a clump of trees. and then the Lumberjack
       wouldn't just wander around aimlessly searching for trees even though it
       saw some when it was just at another tree"""

    def __init__(self, Lumberjack):
        State.__init__(self, "Searching")
        self.lumberjack = Lumberjack

    def entry_actions(self):
        """
        Actions performed when the Lumberjack enters the Searching state, such as setting a random destination.
        """
        BaseFunctions.random_dest(self.lumberjack)

    def do_actions(self):
        pass

    def check_conditions(self):
        """
        Checks conditions to transition to other states. If a tree is found, transitions to the Chopping state.
        If the Lumberjack is hungry, transitions to the Feeding state. If the workday ends, transitions to the Idle state.
        """
        if self.lumberjack.location.get_distance_to(self.lumberjack.destination) < 15:
            location_array = TileFuncs.get_vnn_array(self.lumberjack.world,(self.lumberjack.location), self.lumberjack.view_range)

            for location in location_array:
                test_tile = TileFuncs.get_tile(self.lumberjack.world,location)
                if test_tile.name == "GrassWithCenterTree":
                    self.lumberjack.Tree_tile = test_tile
                    self.lumberjack.tree_id = test_tile.id

                    self.lumberjack.destination = location.copy()
                    return "Chopping"

            BaseFunctions.random_dest(self.lumberjack)

        if self.lumberjack.food < self.lumberjack.hunger_limit:
            return "Feeding"
        if self.lumberjack.world.time >= WORKING_TIME_END:
            return "Idle"

    def exit_actions(self):
        pass


class Chopping(State):
    """
    The Chopping state handles the Lumberjack's behavior when chopping down a tree.
    """
    def __init__(self, Lumberjack):
        State.__init__(self, "Chopping")
        self.lumberjack = Lumberjack

    def entry_actions(self):
        pass

    def do_actions(self):
        pass

    def check_conditions(self):
        """
        Checks conditions to transition to other states. If the tree is fully chopped, transitions to the Delivering state.
        """
        check = TileFuncs.get_tile(self.lumberjack.world,Vector2(self.lumberjack.location))
        if self.lumberjack.location.get_distance_to(self.lumberjack.destination) < 15:
            self.lumberjack.destination = Vector2(self.lumberjack.location)

            if check.name != "GrassWithCenterTree":
                self.lumberjack.hit = 0
                self.lumberjack.update()
                return "Searching"

            self.lumberjack.update()

            if self.lumberjack.hit >= 4:
                self.lumberjack.destination = Vector2(self.lumberjack.location)
                self.lumberjack.update()

                old_tile = TileFuncs.get_tile(self.lumberjack.world,Vector2(self.lumberjack.location))

                darkness = pygame.Surface((32, 32))
                darkness.set_alpha(old_tile.darkness)

                # Replacing "GrassWithCenterTree" with TreePlantedTile will prevent Arborist to plant again,
                # temporarily changed to Grass. This is to be discussed with other team members.
                # new_tile = Tile.TreePlantedTile(self.lumberjack.world, "MinecraftGrass")
                new_tile = Tile.GrassTile(self.lumberjack.world, "MinecraftGrass")

                new_tile.darkness = old_tile.darkness

                new_tile.location = TileFuncs.get_tile_pos(self.lumberjack.world,self.lumberjack.destination)*32
                new_tile.rect.topleft = new_tile.location
                new_tile.color = old_tile.color

                self.lumberjack.world.tile_array[int(new_tile.location.y/32)][int(new_tile.location.x/32)] = new_tile
                self.lumberjack.world.world_surface.blit(new_tile.img, new_tile.location)
                self.lumberjack.world.world_surface.blit(darkness, new_tile.location)

                self.lumberjack.hit = 0

                # del self.lumberjack.world.TreeLocations[str(self.lumberjack.tree_id)]
                return "Delivering"

    def exit_actions(self):
        pass


class Delivering(State):
    """This state will be used solely to deliver wood from wherever the Lumberjack
       got the wood to the closest Lumber yard. maybe all the lumber yards could
       be stored in a dictionary similar to trees, that would be much faster"""

    def __init__(self, Lumberjack):
        State.__init__(self, "Delivering")
        self.lumberjack = Lumberjack

    def entry_actions(self):
        """
        Actions performed when the Lumberjack enters the Delivering state, such as setting the destination to the lumberyard.
        """
        # self.lumberjack.destination = Vector2(self.lumberjack.world.w/2,self.lumberjack.world.h/2)
        self.lumberjack.destination = self.lumberjack.world.lumber_yard[0]

    def do_actions(self):
        pass

    def check_conditions(self):
        """
        Checks conditions to transition to other states. If the wood is successfully delivered, transitions to the Feeding state.
        """
        if self.lumberjack.location.get_distance_to(self.lumberjack.destination) < 15:
            self.lumberjack.world.wood += 5
            return "Feeding"

    def exit_actions(self):
        pass
