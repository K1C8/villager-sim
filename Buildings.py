"""
CS5150 Game AI Final Project
Team Member: Jianyan Chen, Ruidi Huang, Xin Qi
Aug 2024

This program contains classes related to different types of buildings.
Builders build buildings when there are sufficent stones and wood.
"""

import Tile
from aitools.StateMachine import *
from GameEntity import GameEntity
from configuration.world_configuration import WORLD_TILE_SIZE
from gametools.vector2 import Vector2
import glob

from gametools.ImageFuncs import ImageFuncs
import pygame


class Building(GameEntity):
    """
    Represents a general building in the game world. This class serves as a base for specific building types.
    """
    def __init__(self, world, name, pos_tile: Vector2, image_string="Inn"):
        """
        Initializes a building in the game world.

        Args:
            world (World): The game world where the building exists.
            name (str): The name of the building.
            pos_tile (Vector2): The tile position of the building in the world.
            image_string (str): The image filename for the building. Defaults to "Inn".
        """
        GameEntity.__init__(self, world, name, "Buildings/"+image_string, None)
        # Warning: UNTESTED CODE! Treat with caution.
        self.image_funcs = ImageFuncs(32, 32, pygame.image.load("Images/Buildings/TotalImage.png"))
        self.tile_x, self.tile_y = pos_tile
        self.location = Vector2(self.tile_x, self.tile_y)
        # self.location = Vector2(self.tile_x * 32, self.tile_y * 32)

        self.cost = 100
        self.rect = Vector2(32, 32)
        # Placeholder as is
        self.image = pygame.image.load("Images/Buildings/"+image_string+".png")
        
        # Drop-off capabilities for resources
        self.can_drop_fish = False
        self.can_drop_crop = False
        self.can_drop_wood = False
        self.can_drop_stone = False
        self.supports = 0
        self.built_time = 0
        self.time_to_build = 2400

    def update(self):
        """
        Updates the building's state in the world, particularly placing it correctly in the tile array.
        """
        # print("Updating building id:" + str(self.id))
        for tile_x in range(self.image.get_width() // self.world.tile_size):
            for tile_y in range(self.image.get_height() // self.world.tile_size):
                self.world.tile_array[int(self.location.y) + tile_y][int(self.location.x) + tile_x] = (
                    Tile.BuildingTile(self, "MinecraftGrass"))
        self.world.world_surface.blit(self.image, self.location * self.world.tile_size)


class LumberYard(Building):
    """
    Represents a LumberYard building, where wood can be stored and managed.
    """
    SIZE_X = 2
    SIZE_Y = 2
    COST_STONE = 50
    COST_WOOD = 150

    def __init__(self, world, pos_tile: Vector2, image_string="LumberYard"):
        """
        Initializes the LumberYard building.

        Args:
            world (World): The game world where the LumberYard exists.
            pos_tile (Vector2): The tile position of the LumberYard in the world.
            image_string (str): The image filename for the LumberYard. Defaults to "LumberYard".
        """
        Building.__init__(self, world, "Lumber Yard", pos_tile, image_string)

        self.image = self.image_funcs.get_irregular_image(2, 2, 2, 2)
        self.unfinished_image = self.image_funcs.get_irregular_image(2, 2, 0, 2)
        self.finish_image = self.image_funcs.get_irregular_image(2, 2, 2, 2)
        self.image.set_colorkey((255, 0, 255))
        self.finish_image.set_colorkey((255, 0, 255))
        self.unfinished_image.set_colorkey((255, 0, 255))
        self.Held = 0
        self.HeldMax = 50
        self.cost = 100
        self.time_to_build = 4800

        self.world.MAXWood += self.HeldMax
        self.can_drop_wood = True


class Dock(Building):
    """
    Represents a Dock building, where fish can be stored and managed.
    """
    SIZE_X = 2
    SIZE_Y = 2
    COST_STONE = 100
    COST_WOOD = 150
    
    def __init__(self, world, pos_tile: Vector2, image_string="Dock"):
        """
        Initializes the Dock building.

        Args:
            world (World): The game world where the Dock exists.
            pos_tile (Vector2): The tile position of the Dock in the world.
            image_string (str): The image filename for the Dock. Defaults to "Dock".
        """
        Building.__init__(self, world, "Dock", pos_tile, image_string)

        self.image = self.image_funcs.get_irregular_image(2, 2, 2, 0)

        self.unfinished_image = self.image_funcs.get_irregular_image(2, 2, 0, 0)
        self.finish_image = self.image_funcs.get_irregular_image(2, 2, 2, 0)
        self.image.set_colorkey((255, 0, 255))
        self.finish_image.set_colorkey((255, 0, 255))
        self.unfinished_image.set_colorkey((255, 0, 255))

        self.Held = 0
        self.HeldMax = 25
        self.cost = 150
        self.time_to_build = 6000
        
        self.can_drop_fish = True

        self.world.MAXFish += self.HeldMax


class House(Building):
    """
    Represents a House building that increases the population capacity of the village.
    """
    SIZE_X = 1
    SIZE_Y = 1
    COST_STONE = 5
    COST_WOOD = 45

    def __init__(self, world, pos_tile: Vector2, image_string="House"):
        """
        Initializes the House building.

        Args:
            world (World): The game world where the House exists.
            pos_tile (Vector2): The tile position of the House in the world.
            image_string (str): The image filename for the House. Defaults to "House".
        """
        Building.__init__(self, world, "House", pos_tile, image_string)

        self.supports = 5
        self.time_to_build = 600
        # self.cost_wood = 45
        # self.cost_stone = 5

        self.world.MAXpopulation += self.supports


class Manor(Building):
    """
    Represents a Manor building that significantly increases the population capacity of the village.
    """
    SIZE_X = 2
    SIZE_Y = 2
    COST_STONE = 100
    COST_WOOD = 50

    def __init__(self, world, pos_tile: Vector2, image_string="Manor"):
        """
        Initializes the Manor building.

        Args:
            world (World): The game world where the Manor exists.
            pos_tile (Vector2): The tile position of the Manor in the world.
            image_string (str): The image filename for the Manor. Defaults to "Manor".
        """
        Building.__init__(self, world, "Manor", pos_tile, image_string)

        self.image = self.image_funcs.get_irregular_image(2, 2, 2, 4)
        self.finish_image = self.image_funcs.get_irregular_image(2, 2, 2, 4)
        self.unfinished_image = self.image_funcs.get_irregular_image(2, 2, 0, 4)
        self.image.set_colorkey((255, 0, 255))
        self.finish_image.set_colorkey((255, 0, 255))
        self.unfinished_image.set_colorkey((255, 0, 255))

        self.supports = 10
        self.time_to_build = 2400
        # self.cost_stone = 100
        # self.cost_wood = 50

        self.world.MAXpopulation += self.supports


class TownCenter(Building):
    """
    Represents a TownCenter building that serves as a central hub for resources and population.
    """
    SIZE_X = 2
    SIZE_Y = 2
    COST_STONE = 200
    COST_WOOD = 200

    def __init__(self, world, pos_tile: Vector2, image_string="TownCenter"):
        """
        Initializes the TownCenter building.

        Args:
            world (World): The game world where the TownCenter exists.
            pos_tile (Vector2): The tile position of the TownCenter in the world.
            image_string (str): The image filename for the TownCenter. Defaults to "TownCenter".
        """
        print("Pos_tile at TownCenter.__init__ is " + str(pos_tile))
        Building.__init__(self, world, "TownCenter", pos_tile, image_string)
       
        # Setup images for different stages of construction
        self.image = self.image_funcs.get_irregular_image(2, 2, 2, 6)
        self.finish_image = self.image_funcs.get_irregular_image(2, 2, 2, 6)
        self.unfinished_image = self.image_funcs.get_irregular_image(2, 2, 0, 6)
        self.image.set_colorkey((255, 0, 255))
        self.finish_image.set_colorkey((255, 0, 255))
        self.unfinished_image.set_colorkey((255, 0, 255))

        # Setting up resource and population support
        self.can_drop_fish = True
        self.can_drop_crop = True
        self.can_drop_wood = True
        self.can_drop_stone = True
        
        self.supports = 5
        self.cost = 500
        self.time_to_build = 9000
        # self.cost_wood = 200
        # self.cost_stone = 200

        self.world.MAXpopulation += self.supports
        self.world.MAXWood += 100
        self.world.MAXFish += 100
        self.world.MAXCrop += 100
        self.world.MAXStone += 100


class UnderConstruction2x2(Building):
    """
    Represents a placeholder for buildings that are currently under construction.
    """
    SIZE_X = 2
    SIZE_Y = 2

    def __init__(self, world, pos_tile: Vector2, image_string, will_be):
        """
        Initializes the UnderConstruction2x2 building placeholder.

        Args:
            world (World): The game world where the building exists.
            pos_tile (Vector2): The tile position of the building in the world.
            image_string (str): The image filename for the building under construction.
            will_be (Building): The building type that this placeholder will become once construction is complete.
        """
        Building.__init__(self, world, "Under Construction", pos_tile, image_string)

        self.image = self.image_funcs.get_irregular_image(2, 2, 0, 2)
        self.will_be = will_be
        self.ttb = 30.0
        self.max_ttb = 30.0

    def create(self):
        """
        Finalizes the construction and replaces this placeholder with the actual building.
        """
        self.world.add_built(self.will_be, self.location)
        self.world.remove_entity(self)


class StoreShed(Building):
    """
    Represents a Store Shed building, a simple storage structure.
    """
    def __init__(self, world, pos_tile: Vector2, image_string):
        """
        Initializes the Store Shed building.

        Args:
            world (World): The game world where the Store Shed exists.
            pos_tile (Vector2): The tile position of the Store Shed in the world.
            image_string (str): The image filename for the Store Shed.
        """
        Building.__init__(self, world, "Store Shed", pos_tile, image_string)


class Barn(Building):
    """
    Represents a Barn building, where crops can be stored and managed.
    """
    SIZE_X = 2
    SIZE_Y = 2
    COST_STONE = 100
    COST_WOOD = 50

    def __init__(self, world, pos_tile: Vector2, image_string="Barn"):
        """
        Initializes the Barn building.

        Args:
            world (World): The game world where the Barn exists.
            pos_tile (Vector2): The tile position of the Barn in the world.
            image_string (str): The image filename for the Barn. Defaults to "Barn".
        """
        Building.__init__(self, world, "Barn", pos_tile, image_string)

        self.image = self.image_funcs.get_irregular_image(2, 2, 2, 12)
        self.finish_image = self.image_funcs.get_irregular_image(2, 2, 2, 12)
        self.unfinished_image = self.image_funcs.get_irregular_image(2, 2, 0, 12)
        self.image.set_colorkey((255, 0, 255))
        self.finish_image.set_colorkey((255, 0, 255))
        self.unfinished_image.set_colorkey((255, 0, 255))
        self.Held = 0
        self.HeldMax = 500
        self.time_to_build = 3600
        # self.cost_stone = 100
        # self.cost_wood = 50

        self.world.MAXCrop += self.HeldMax
        self.can_drop_crop = True


class Stonework(Building):
    """
    Represents a Stonework building, where stone can be stored and managed.
    """
    SIZE_X = 2
    SIZE_Y = 2
    COST_STONE = 150
    COST_WOOD = 50

    def __init__(self, world, pos_tile: Vector2, image_string="Stonework"):
        """
        Initializes the Stonework building.

        Args:
            world (World): The game world where the Stonework exists.
            pos_tile (Vector2): The tile position of the Stonework in the world.
            image_string (str): The image filename for the Stonework. Defaults to "Stonework".
        """
        Building.__init__(self, world, "Stonework", pos_tile, image_string)

        self.image = self.image_funcs.get_irregular_image(2, 2, 2, 10)
        self.finish_image = self.image_funcs.get_irregular_image(2, 2, 2, 10)
        self.unfinished_image = self.image_funcs.get_irregular_image(2, 2, 0, 10)
        self.image.set_colorkey((255, 0, 255))
        self.finish_image.set_colorkey((255, 0, 255))
        self.unfinished_image.set_colorkey((255, 0, 255))
        self.Held = 0
        self.HeldMax = 500
        self.time_to_build = 3600
        # self.cost_stone = 150
        # self.cost_wood = 50

        self.world.MAXStone += self.HeldMax
        self.can_drop_stone = True


class FishMarket(Building):
    """
    Represents a Fish Market building, where fish can be stored and managed.
    """
    SIZE_X = 2
    SIZE_Y = 2
    COST_STONE = 50
    COST_WOOD = 150

    def __init__(self, world, pos_tile: Vector2, image_string="FishMarket"):
        """
        Initializes the Fish Market building.

        Args:
            world (World): The game world where the Fish Market exists.
            pos_tile (Vector2): The tile position of the Fish Market in the world.
            image_string (str): The image filename for the Fish Market. Defaults to "FishMarket".
        """
        Building.__init__(self, world, "FishMarket", pos_tile, image_string)

        self.image = self.image_funcs.get_irregular_image(2, 2, 2, 8)
        self.finish_image = self.image_funcs.get_irregular_image(2, 2, 2, 8)
        self.unfinished_image = self.image_funcs.get_irregular_image(2, 2, 0, 8)
        self.image.set_colorkey((255, 0, 255))
        self.finish_image.set_colorkey((255, 0, 255))
        self.unfinished_image.set_colorkey((255, 0, 255))
        self.Held = 0
        self.HeldMax = 500
        self.time_to_build = 7200
        # self.cost_wood = 150
        # self.cost_stone = 50

        self.world.MAXFish += self.HeldMax
        self.can_drop_fish = True
