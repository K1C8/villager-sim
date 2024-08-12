"""
CS5150 Game AI Final Project
Team Member: Jianyan Chen, Ruidi Huang, Xin Qi
Aug 2024

This program defines the Arborist class for villagers in the game.
Arborist plants trees in the game.
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
from async_funcs.entity_consumption import consume_func_villager
import math
import pygame
import random
import TileFuncs
import BaseFunctions


class Arborist(GameEntity):
    """
    Arborist is a specialized GameEntity responsible for planting trees in the game world.
    The Arborist transitions between states such as Planting, Feeding, and Idle.
    """
    def __init__(self, world, image_string):
        """
        Initializes an Arborist entity in the game world.

        Args:
            world (World): The game world in which the Arborist exists.
            image_string (str): The path to the image representing the Arborist.
        """
        # Initializing the class
        GameEntity.__init__(self, world, "Arborist", "Entities/"+image_string, consume_func_villager)

        # Creating the states
        planting_state = Arborist_Planting(self)
        feeding_state = Feeding(self)
        idle_state = Idle(self)

        # Adding states to the brain
        self.brain.add_state(planting_state)
        self.brain.add_state(feeding_state)
        self.brain.add_state(idle_state)

        self.max_speed = 80.0 * (1.0 / 60.0)
        self.speed = self.max_speed
        self.base_speed = self.speed
        self.hunger_limit = 40

        self.worldSize = world.world_size
        self.TileSize = self.world.tile_size
        self.primary_state = "Planting"

        # animation variables
        self.animation = Ani(6,10)
        self.pic = pygame.image.load("Images/Entities/map.png")
        self.img_func = ImageFuncs(18, 17,self.pic)
        self.sprites = self.img_func.get_images(6,0,0)
        self.hit = 0
        self.update()

    def update(self):
        """
        Updates the Arborist's current image based on the animation state
        and increments the hit counter when the animation finishes.
        """
        # Updates image every 10 cycles and adds 1 to the 4 hit dig
        self.image = self.sprites[self.animation.get_frame()]
        self.image.set_colorkey((255,0,255))
        if self.animation.finished == True:
            self.hit += 1
            self.animation.finished = False


class Arborist_Planting(State):
    """
    Arborist_Planting is a state where the Arborist plants trees in the game world.
    """
    def __init__(self, Arborist):
        """
        Initializes the Planting state.

        Args:
            Arborist (Arborist): The Arborist entity associated with this state.
        """
        State.__init__(self, "Planting")
        self.arborist = Arborist

    def check_conditions(self):
        """
        Checks if the conditions to continue planting or transition to another state are met.

        Returns:
            str: The next state to transition to, if any.
        """
        # Check if Arborist has reached its destination
        if self.arborist.location.get_distance_to(self.arborist.destination) < 15:
            self.arborist.destination = Vector2(self.arborist.location)
            self.arborist.update()

        # Transition to Feeding state if Arborist is hungry
        if self.arborist.food < self.arborist.hunger_limit:
            return "Feeding"

        # Transition to Idle state if the workday is over
        if self.arborist.world.time >= WORKING_TIME_END:
            return "Idle"

    def do_actions(self):
        """
        Performs actions associated with planting trees.
        """
        # Plant a seed if Arborist is at the destination and the tile is plantable
        if self.arborist.location == self.arborist.destination and self.arborist.hit >= 4 and TileFuncs.get_tile(
                self.arborist.world,self.arborist.location).plantable == 1:
            self.plant_seed()

        # Move to a random destination if the current tile is not plantable
        if self.arborist.location == self.arborist.destination and self.arborist.hit != 4 and TileFuncs.get_tile(
                self.arborist.world, self.arborist.location).plantable != 1:
            BaseFunctions.random_dest(self.arborist)

    def plant_seed(self):
        """
        Plants a tree on the current tile if it is plantable.
        """
        # Function for planting trees

        # Test to see if the tile the arborist is on is a tile that a tree can be planted on
        if TileFuncs.get_tile(self.arborist.world,self.arborist.location).plantable == 1:
            self.arborist.hit = 0
            self.arborist.update()
            old_tile = TileFuncs.get_tile(self.arborist.world,Vector2(self.arborist.location))

            # Prepare the new tile for the tree
            darkness = pygame.Surface((32, 32))
            darkness.set_alpha(old_tile.darkness)

            new_tile = Tile.Baby_Tree(self.arborist.world, "GrassWithCenterTree")

            new_tile.darkness = old_tile.darkness

            new_tile.location = TileFuncs.get_tile_pos(self.arborist.world,self.arborist.destination)*32
            new_tile.rect.topleft = new_tile.location
            new_tile.color = old_tile.color

            # Update the world with the new tile
            self.arborist.world.tile_array[int(new_tile.location.y/32)][int(new_tile.location.x/32)] = new_tile
            self.arborist.world.world_surface.blit(new_tile.img, new_tile.location)
            self.arborist.world.world_surface.blit(darkness, new_tile.location)

        # Goes to a random destination no matter what
        self.arborist.hit = 0
        BaseFunctions.random_dest(self.arborist)

    def entry_actions(self):
        """
        Defines actions to be taken when entering the Planting state.
        """
        BaseFunctions.random_dest(self.arborist)
