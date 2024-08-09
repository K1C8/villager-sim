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

    def __init__(self, world):
        self.world = world

    def draw_path(self, screen, start_pos, end_pos, color):
        pygame.draw.line(screen, color, start_pos, end_pos, 2)  # Draw a red line

    def render(self, screen):
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
            start_pos = (int(entity.world_location.x), int(entity.world_location.y))
            end_pos = (int(entity.destination.x + entity.world.world_position.x),
                        int(entity.destination.y + entity.world.world_position.y))
            self.draw_path(screen, start_pos, end_pos, color)
        
        