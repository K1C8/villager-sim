import asyncio

from World import *
from aitools.StateMachine import *
from gametools.vector2 import *
import TileFuncs
import pygame
from pygame.locals import *

# TODO: Clean and add doctrings


class GameEntity(object):
    def __init__(self, world, name, image_string, consume_func):

        self.world = world
        self.name = name

        self.image = pygame.image.load("Images/"+image_string+".png")
        self.orientation = 0
        
        try:
            self.image.set_colorkey((255, 0, 255))
        except AttributeError:
            pass
        
        self.location = Vector2(0, 0)
        self.world_location = Vector2(0, 0)
        self.destination = Vector2(0, 0)
        
        self.speed = 0.

        self.land_based = True
        self.base_speed = self.speed
        
        self.food = 70
        self.water = 70
        self.energy = 70
        self.active_info = False
        self.consume_func = consume_func
        # self.consume_func(self)

        self.brain = StateMachine()

        self.id = 0

        self.tp = 1.0

        # TODO (wazzup771@gmail.com | Nick Wayne): Not sure if these belong in the World class either
        self.info_bar = pygame.image.load("Images/Entities/info_bar.png").convert()
        self.info_bar.set_colorkey((255, 0, 255))
        self.f_high = (50, 200, 50)
        self.f_low = (255, 0, 0)
        self.w_high = (0, 0, 255)
        self.w_low = (76, 70, 50)
        self.e_high = (0, 255, 0)
        self.e_low = (50, 50, 0)

    def render(self, surface):
        x, y = self.world_location
        w, h = self.image.get_size()
        pos = (x - (w / 2), y - (h / 2))
        surface.blit(self.image, pos)

    def check_speed(self):
        if TileFuncs.get_tile(self.world, self.location).name in ["AndrewSmoothStone", "MinecraftSnow"]:
            self.speed = 0.5 * self.base_speed
        else:
            self.speed = self.base_speed

    # TODO(wazzup771@gmail.com | Nick Wayne): This function doesn't belong in the world class, perhaps the GameEntity
    #  class.
    def render_info_bar(self, surface, entity):
        lst = [self.f_high, self.f_low, self.w_high, self.w_low, self.e_high, self.e_low]
        lst2 = [entity.food, entity.water, entity.energy]
        surface.blit(self.info_bar, (entity.world_location.x + 10, entity.world_location.y - 20))
        for i in range(3):
            t = lst2[i] / 100.
            r = self.lerp(lst[2 * i][0], lst[2 * i + 1][0], t)
            g = self.lerp(lst[2 * i][1], lst[2 * i + 1][1], t)
            b = self.lerp(lst[2 * i][2], lst[2 * i + 1][2], t)
            pygame.draw.rect(surface, (r, g, b),
                             pygame.Rect((entity.world_location.x + 20, entity.world_location.y - 14 + (i * 7)),
                                         (int(40 * t), 4)))

        # if DEBUG_MODE:
        debug_font = pygame.font.SysFont(None, 16)
        debug_ent_active_state_string = "State: " + str(entity.brain.active_state.name)
        ent_active_state_surface = debug_font.render(debug_ent_active_state_string, True, (255, 255, 255))
        surface.blit(ent_active_state_surface, (entity.world_location.x + 10, entity.world_location.y + 15))

    def lerp(self, v1, v2, t):
        return (1 - t) * v2 + t * v1

    def process(self, time_passed):
        self.brain.think()
        self.world_location = self.location + self.world.world_position


        self.check_speed()

        if self.speed > 0. and self.location != self.destination:
            vec_to_destination = self.destination - self.location
            distance_to_destination = vec_to_destination.get_length()
            heading = vec_to_destination.get_normalized()
            travel_distance = min(distance_to_destination, self.speed)
            self.location += travel_distance * heading * self.speed

    def death(self):
        self.world.delete_entity(self)

