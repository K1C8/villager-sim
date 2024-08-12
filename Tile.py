"""
CS5150 Game AI Final Project
Team Member: Jianyan Chen, Ruidi Huang, Xin Qi
Aug 2024

This program defines class for all tiles in game.
"""

from random import randint
import pygame
from gametools.vector2 import Vector2


class Tile(object):
    """
    Base class for all tile types in the game.

    Attributes:
        world (World): The game world instance the tile belongs to.
        name (str): The name of the tile.
        img (pygame.Surface): The image associated with the tile.
        location (Vector2): The position of the tile in the world.
        walkable (bool): Indicates if entities can walk on this tile.
        fishable (bool): Indicates if entities can fish on this tile.
        plantable (bool): Indicates if trees can be planted on this tile.
        tillable (bool): Indicates if the tile can be tilled for farming.
        crop_plantable (bool): Indicates if crops can be planted on this tile.
        crop_waterable (bool): Indicates if the tile can be watered.
        crop_harvestable (bool): Indicates if crops can be harvested from this tile.
        buildable (bool): Indicates if buildings can be placed on this tile.
        buildable_w (bool): Indicates if water-based buildings can be placed on this tile.
        darkness (int): Represents the darkness level on the tile.
        watered_times (int): Tracks the number of times the tile has been watered.
        watered_req (int): Number of times the tile needs to be watered to mature.
        id (int): Unique identifier for the tile.
        rect (pygame.Rect): The rectangular area of the tile.
        cost (int): Movement cost associated with the tile (lower is easier to traverse).
    """
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
        """
        Renders the tile on the given screen.

        Args:
            screen (pygame.Surface): The screen to render the tile on.
        """
        screen.blit(self.img, self.location)


class GrassTile(Tile):
    """
    A grass tile, suitable for walking, building, planting, and tilling.
    """
    def __init__(self, world, tile_name):
        Tile.__init__(self, world, tile_name)
        self.walkable = True
        self.buildable = True
        self.plantable = True
        self.tillable = True
        self.cost = 1  # Easy to walk

class WaterTile(Tile):
    """
    A water tile, suitable for fishing and building water-based structures.
    """
    def __init__(self, world, tile_name):
        Tile.__init__(self, world, tile_name)
        self.buildable_w = True
        self.fishable = True
        self.cost = 100

class DeepWaterTile(Tile):
    """
    A deep water tile, not suitable for walking but can have water-based buildings.
    """
    def __init__(self, world, tile_name):
        Tile.__init__(self, world, tile_name)
        self.buildable_w = True
        self.cost = 100

class SmoothStoneTile(Tile):
    """
    A smooth stone tile, suitable for walking and building.
    """
    def __init__(self, world, tile_name):
        Tile.__init__(self, world, tile_name)
        self.walkable = True
        self.buildable = True
        self.cost = 3

class CobblestoneTile(Tile):
    """
    A cobblestone tile, harder to walk on but suitable for building.
    """
    def __init__(self, world, tile_name):
        Tile.__init__(self, world, tile_name)
        self.walkable = True
        self.buildable = True
        self.cost = 5

class DirtTile(Tile):
    """
    A dirt tile, suitable for walking, building, and tilling.
    """
    def __init__(self, world, tile_name):
        Tile.__init__(self, world, tile_name)
        self.walkable = True
        self.buildable = True
        self.tillable = True
        self.cost = 1

class BeachTile(Tile):
    """
    A beach tile, suitable for walking and building.
    """
    def __init__(self, world, tile_name):
        Tile.__init__(self, world, tile_name)
        self.walkable = True
        self.buildable = True
        self.cost = 1

class Baby_Tree(Tile):
    """
    A baby tree tile, representing a young tree that can be walked on.
    """
    def __init__(self, world, tile_name):
        Tile.__init__(self, world, tile_name)
        self.walkable = True
        self.cost = 1

class TreePlantedTile(Tile):
    """
    A tile with a planted tree, indicating the presence of a tree.
    """
    def __init__(self, world, tile_name):
        Tile.__init__(self, world, tile_name)
        self.walkable = True
        self.Taken = False
        self.cost = 1

class SnowTile(Tile):
    """
    A snow tile, which is harder to walk on.
    """
    def __init__(self, world, tile_name):
        Tile.__init__(self, world, tile_name)
        self.walkable = True
        self.cost = 10


class BuildingTile(Tile):
    """
    A tile representing a building, suitable for walking.
    """
    def __init__(self, world, tile_name):
        Tile.__init__(self, world, tile_name)
        self.walkable = True
        self.cost = 1

class SoilTile(Tile):
    """
    A soil tile, suitable for walking and planting crops.
    """
    def __init__(self, world, tile_name):
        Tile.__init__(self, world, tile_name)
        self.walkable = True
        self.crop_plantable = True
        self.cost = 1


class ShootFieldTile(Tile):
    """
    A tile representing a crop field that is in the process of growing.
    """
    def __init__(self, world, tile_name):
        Tile.__init__(self, world, tile_name)
        self.walkable = True
        self.cost = 1
        self.watered_times = 0
        self.watered_req = randint(1, 2)
        self.crop_waterable = True


class MatureFieldTile(Tile):
    """
    A tile representing a mature crop field, ready for harvest.
    """
    def __init__(self, world, tile_name):
        Tile.__init__(self, world, tile_name)
        self.walkable = True
        self.crop_harvestable = True
        self.cost = 1
