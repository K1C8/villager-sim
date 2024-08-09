import pygame
from Lumberjack import Lumberjack
from Angler import Angler
from Arborist import Arborist
from Builder import Builder
from Explorer import Explorer
from Farmer import Farmer
from FishingShip import FishingShip


class Visualizer:

    def __init__(self, world):
        self.world = world

    def draw_path(self, screen, start_pos, end_pos):
        pygame.draw.line(screen, (255, 0, 0), start_pos, end_pos, 2)  # Draw a red line

    def render(self, screen):
        for entity in self.world.entities.values():
            if isinstance(entity, Lumberjack):
                start_pos = (int(entity.world_location.x), int(entity.world_location.y))
                end_pos = (int(entity.destination.x + entity.world.world_position.x),
                        int(entity.destination.y + entity.world.world_position.y))
                self.draw_path(screen, start_pos, end_pos)