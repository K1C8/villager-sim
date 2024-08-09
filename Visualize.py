"""
CS5150 Game AI Final Project
Team Member: Jianyan Chen, Ruidi Huang, Xin Qi
Aug 2024
This programs contain visualizer class for showing the destination for villagers
and their expected moving routes.
"""
import pygame
from Angler import Angler
from Arborist import Arborist
from Builder import Builder
from Explorer import Explorer
from Farmer import Farmer
from FishingShip import FishingShip
from Lumberjack import Lumberjack
from configuration.world_configuration import LINE_COLOR


class Visualizer:
    """
    A class to visualize the paths of entities in the game world.

    Attributes:
        world (World): The game world containing entities.
    """
    def __init__(self, world):
        """
        Initializes the Visualizer with a reference to the game world.

        Args:
            world (World): The game world containing entities.
        """
        self.world = world

    def draw_path(self, screen, start_pos, end_pos, color):
        """
        Draws a path between two points on the screen.

        Args:
            screen (pygame.Surface): The surface on which to draw the path.
            start_pos (tuple): The starting position (x, y) of the path.
            end_pos (tuple): The ending position (x, y) of the path.
            color (tuple): The color of the path, defined as an (R, G, B) tuple.
        """
        pygame.draw.line(screen, color, start_pos, end_pos, 2)

    def render(self, screen):
        """
        Renders the paths for all entities in the world on the screen.

        Args:
            screen (pygame.Surface): The surface on which to render the paths.
        """
        for entity in self.world.entities.values():
            match entity:
                case Lumberjack():
                    color = LINE_COLOR[0]
                case Angler():
                    color = LINE_COLOR[1]
                case Arborist():
                    color = LINE_COLOR[2]
                case Builder():
                    color = LINE_COLOR[3]
                case Explorer():
                    color = LINE_COLOR[4]
                case Farmer():
                    color = LINE_COLOR[5]
                case FishingShip():
                    color = LINE_COLOR[6]
                case _:
                    color = (0, 0, 0) # default color: Black
            
            # Calculate the start and end positions for the path
            start_pos = (int(entity.world_location.x), int(entity.world_location.y))
            end_pos = (int(entity.destination.x + entity.world.world_position.x),
                        int(entity.destination.y + entity.world.world_position.y))

            # Draw the path on the screen
            self.draw_path(screen, start_pos, end_pos, color)
        
        