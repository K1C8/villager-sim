from aitools.StateMachine import *
from GameEntity import GameEntity
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
        # Placeholder as is
        self.image = pygame.image.load("Images/Buildings/"+image_string+".png")
        
        self.can_drop_fish = False
        self.can_drop_crop = False
        self.can_drop_wood = False
        self.can_drop_stone = False
        self.supports = 0


class LumberYard(Building):
    def __init__(self, world, pos_tile: Vector2, image_string="LumberYard"):
        Building.__init__(self, world, "Lumber Yard", pos_tile, image_string)

        self.image = self.image_funcs.get_irregular_image(2, 2, 2, 2)
        self.Held = 0
        self.HeldMax = 50
        self.cost = 100

        self.world.MAXwood += self.HeldMax
        self.can_drop_wood = True


class Dock(Building):
    
    def __init__(self, world, pos_tile: Vector2, image_string="Dock"):
        Building.__init__(self, world, "Dock", pos_tile, image_string)

        self.image = self.image_funcs.get_irregular_image(2, 2, 2, 0)

        self.Held = 0
        self.HeldMax = 25
        self.cost = 150
        
        self.can_drop_fish = True

        self.world.MAXfood += self.HeldMax


class House(Building):
    def __init__(self, world, pos_tile: Vector2, image_string="House"):
        Building.__init__(self, world, "House", pos_tile, image_string)

        self.supports = 5
        self.cost_wood = 45
        self.cost_stone = 5

        self.world.MAXpopulation += self.supports


class Manor(Building):
    def __init__(self, world, pos_tile: Vector2, image_string="Manor"):
        Building.__init__(self, world, "Manor", pos_tile, image_string)

        self.image = self.image_funcs.get_irregular_image(2, 2, 2, 4)

        self.supports = 15
        self.cost_stone = 100
        self.cost_wood = 50

        self.world.MAXpopulation += self.supports
        
class TownCenter(Building):
    def __init__(self, world, pos_tile: Vector2, image_string="TownCenter"):
        print("Pos_tile at TownCenter.__init__ is " + str(pos_tile))
        Building.__init__(self, world, "TownCenter", pos_tile, image_string)
       
        self.image = self.image_funcs.get_irregular_image(2, 2, 2, 6)
        self.image.set_colorkey((255, 0, 255))

        self.can_drop_fish = True
        self.can_drop_crop = True
        self.can_drop_wood = True
        self.can_drop_stone = True
        
        self.supports = 15
        self.cost = 500
        self.cost_wood = 200
        self.cost_stone = 200

        self.world.MAXpopulation += self.supports
        self.world.MAXWood += 500
        self.world.MAXFish += 500
        self.world.MAXCrop += 500
        self.world.MAXStone += 500


class UnderConstruction(Building):
    def __init__(self, world, pos_tile: Vector2, image_string, will_be):
        Building.__init__(self, world, "Under Construction", pos_tile, image_string)
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
    def __init__(self, world, pos_tile: Vector2, image_string="Barn"):
        Building.__init__(self, world, "Barn", pos_tile, image_string)

        self.image = self.image_funcs.get_irregular_image(2, 2, 2, 2)
        self.Held = 0
        self.HeldMax = 500
        self.cost_stone = 100
        self.cost_wood = 50

        self.world.MAXwood += self.HeldMax
        self.can_drop_crop = True


class Stonework(Building):
    def __init__(self, world, pos_tile: Vector2, image_string="Stonework"):
        Building.__init__(self, world, "Stonework", pos_tile, image_string)

        self.image = self.image_funcs.get_irregular_image(2, 2, 2, 2)
        self.Held = 0
        self.HeldMax = 500
        self.cost_stone = 150
        self.cost_wood = 50

        self.world.MAXstone += self.HeldMax
        self.can_drop_stone = True


class FishMarket(Building):
    def __init__(self, world, pos_tile: Vector2, image_string="FishMarket"):
        Building.__init__(self, world, "FishMarket", pos_tile, image_string)

        self.image = self.image_funcs.get_irregular_image(2, 2, 2, 2)
        self.Held = 0
        self.HeldMax = 500
        self.cost_wood = 150
        self.cost_stone = 50

        self.world.MAXstone += self.HeldMax
        self.can_drop_fish = True
