from random import randint

import pygame

from gametools.vector2 import Vector2


class Tile(object):
    def __init__(self, world, tile_name="NULL"):
        self.world = world
        self.name = tile_name
        self.img = pygame.image.load("Images/Tiles/"+tile_name+".png").convert()
        self.location = Vector2(0, 0)
        self.walkable = False
        self.fishable = False
        self.plantable = False
        self.tillable = False
        self.crop_plantable = False
        self.crop_waterable = False
        self.crop_harvestable = False
        self.buildable = False
        self.buildable_w = False
        self.darkness = 0
        self.watered_times = 0
        self.watered_req = 0

        self.id = 0
        self.rect = pygame.Rect((0, 0), self.img.get_size())
        self.cost = 100  # Default to infinite cost if not walkable

    def render(self, screen):
        screen.blit(self.img, self.location)


class GrassTile(Tile):
    def __init__(self, world, tile_name):
        Tile.__init__(self, world, tile_name)
        self.walkable = True
        self.buildable = True
        self.plantable = True
        self.tillable = True
        self.cost = 1  # Easy to walk

class WaterTile(Tile):
    def __init__(self, world, tile_name):
        Tile.__init__(self, world, tile_name)
        self.buildable_w = True
        self.fishable = True
        self.cost = 100

class DeepWaterTile(Tile):
    def __init__(self, world, tile_name):
        Tile.__init__(self, world, tile_name)
        self.buildable_w = True
        self.cost = 100

class SmoothStoneTile(Tile):
    def __init__(self, world, tile_name):
        Tile.__init__(self, world, tile_name)
        self.walkable = True
        self.buildable = True
        self.cost = 3

class CobblestoneTile(Tile):
    def __init__(self, world, tile_name):
        Tile.__init__(self, world, tile_name)
        self.walkable = True
        self.buildable = True
        self.cost = 5

class DirtTile(Tile):
    def __init__(self, world, tile_name):
        Tile.__init__(self, world, tile_name)
        self.walkable = True
        self.buildable = True
        self.tillable = True
        self.cost = 1

class BeachTile(Tile):
    def __init__(self, world, tile_name):
        Tile.__init__(self, world, tile_name)
        self.walkable = True
        self.buildable = True
        self.cost = 1

class Baby_Tree(Tile):
    def __init__(self, world, tile_name):
        Tile.__init__(self, world, tile_name)
        self.walkable = True
        self.cost = 1

class TreePlantedTile(Tile):
    def __init__(self, world, tile_name):
        Tile.__init__(self, world, tile_name)
        self.walkable = True
        self.Taken = False
        self.cost = 1

class SnowTile(Tile):
    def __init__(self, world, tile_name):
        Tile.__init__(self, world, tile_name)
        self.walkable = True
        self.cost = 10


class BuildingTile(Tile):
    def __init__(self, world, tile_name):
        Tile.__init__(self, world, tile_name)
        self.walkable = True
        self.cost = 1

class SoilTile(Tile):
    def __init__(self, world, tile_name):
        Tile.__init__(self, world, tile_name)
        self.walkable = True
        self.crop_plantable = True
        self.cost = 1


class ShootFieldTile(Tile):
    def __init__(self, world, tile_name):
        Tile.__init__(self, world, tile_name)
        self.walkable = True
        self.cost = 1
        self.watered_times = 0
        self.watered_req = randint(1, 2)
        self.crop_waterable = True


class MatureFieldTile(Tile):
    def __init__(self, world, tile_name):
        Tile.__init__(self, world, tile_name)
        self.walkable = True
        self.crop_harvestable = True
        self.cost = 1
