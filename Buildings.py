import Tile
from aitools.StateMachine import *
from GameEntity import GameEntity
from configuration.world_configuration import WORLD_TILE_SIZE
from gametools.vector2 import Vector2
import glob

from gametools.ImageFuncs import ImageFuncs
import pygame


class Building(GameEntity):
    def __init__(self, world, name, pos_tile: Vector2, image_string="Inn"):
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
        
        self.can_drop_fish = False
        self.can_drop_crop = False
        self.can_drop_wood = False
        self.can_drop_stone = False
        self.supports = 0
        self.built_time = 0
        self.time_to_build = 2400

    def update(self):
        # print("Updating building id:" + str(self.id))
        for tile_x in range(self.image.get_width() // self.world.tile_size):
            for tile_y in range(self.image.get_height() // self.world.tile_size):
                self.world.tile_array[int(self.location.y) + tile_y][int(self.location.x) + tile_x] = (
                    Tile.BuildingTile(self, "MinecraftGrass"))
        self.world.world_surface.blit(self.image, self.location * self.world.tile_size)


class LumberYard(Building):
    SIZE_X = 2
    SIZE_Y = 2
    COST_STONE = 50
    COST_WOOD = 150

    def __init__(self, world, pos_tile: Vector2, image_string="LumberYard"):
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
    SIZE_X = 2
    SIZE_Y = 2
    COST_STONE = 100
    COST_WOOD = 150
    
    def __init__(self, world, pos_tile: Vector2, image_string="Dock"):
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
    SIZE_X = 1
    SIZE_Y = 1
    COST_STONE = 5
    COST_WOOD = 45

    def __init__(self, world, pos_tile: Vector2, image_string="House"):
        Building.__init__(self, world, "House", pos_tile, image_string)

        self.supports = 5
        self.time_to_build = 600
        # self.cost_wood = 45
        # self.cost_stone = 5

        self.world.MAXpopulation += self.supports


class Manor(Building):
    SIZE_X = 2
    SIZE_Y = 2
    COST_STONE = 100
    COST_WOOD = 50

    def __init__(self, world, pos_tile: Vector2, image_string="Manor"):
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
    SIZE_X = 2
    SIZE_Y = 2
    COST_STONE = 200
    COST_WOOD = 200

    def __init__(self, world, pos_tile: Vector2, image_string="TownCenter"):
        print("Pos_tile at TownCenter.__init__ is " + str(pos_tile))
        Building.__init__(self, world, "TownCenter", pos_tile, image_string)
       
        self.image = self.image_funcs.get_irregular_image(2, 2, 2, 6)
        self.finish_image = self.image_funcs.get_irregular_image(2, 2, 2, 6)
        self.unfinished_image = self.image_funcs.get_irregular_image(2, 2, 0, 6)
        self.image.set_colorkey((255, 0, 255))
        self.finish_image.set_colorkey((255, 0, 255))
        self.unfinished_image.set_colorkey((255, 0, 255))

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
    SIZE_X = 2
    SIZE_Y = 2

    def __init__(self, world, pos_tile: Vector2, image_string, will_be):
        Building.__init__(self, world, "Under Construction", pos_tile, image_string)

        self.image = self.image_funcs.get_irregular_image(2, 2, 0, 2)
        self.will_be = will_be
        self.ttb = 30.0
        self.max_ttb = 30.0

    def create(self):
        self.world.add_built(self.will_be, self.location)
        self.world.remove_entity(self)


class StoreShed(Building):

    def __init__(self, world, pos_tile: Vector2, image_string):
        Building.__init__(self, world, "Store Shed", pos_tile, image_string)


class Barn(Building):
    SIZE_X = 2
    SIZE_Y = 2
    COST_STONE = 100
    COST_WOOD = 50

    def __init__(self, world, pos_tile: Vector2, image_string="Barn"):
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
    SIZE_X = 2
    SIZE_Y = 2
    COST_STONE = 150
    COST_WOOD = 50

    def __init__(self, world, pos_tile: Vector2, image_string="Stonework"):
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
    SIZE_X = 2
    SIZE_Y = 2
    COST_STONE = 50
    COST_WOOD = 150

    def __init__(self, world, pos_tile: Vector2, image_string="FishMarket"):
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
