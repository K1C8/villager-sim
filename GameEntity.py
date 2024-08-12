"""
CS5150 Game AI Final Project
Team Member: Jianyan Chen, Ruidi Huang, Xin Qi
Aug 2024

This program defines the GameEntity class for any entity in the game world.
"""

from World import *
from aitools.StateMachine import *
from gametools.vector2 import *
import TileFuncs
import pygame
from pygame.locals import *
from PathFinding import a_star_search_nx, create_graph
from configuration.world_configuration import DEBUG


class GameEntity(object):
    """
    The GameEntity class represents any entity in the game world, such as villagers or buildings.
    It handles the basic properties and behaviors of an entity, including its position, image, 
    speed, and the state machine controlling its actions.
    """
    def __init__(self, world, name, image_string, consume_func):
        """
        Initializes a GameEntity object with basic attributes such as position, image, and state.

        Args:
            world (World): The game world the entity exists in.
            name (str): The name of the entity.
            image_string (str): The path to the entity's image file.
            consume_func (function): A function to handle the entity's consumption of resources.
        """
        self.world = world
        self.name = name

        # Load the image and set transparency color key
        self.image = pygame.image.load("Images/"+image_string+".png")
        self.orientation = 0
        
        try:
            self.image.set_colorkey((255, 0, 255))
        except AttributeError:
            pass
        
        # Position and movement attributes
        self.location = Vector2(0, 0)
        self.world_location = Vector2(0, 0)
        self.destination = Vector2(0, 0)
        self.tile_location_x = int(self.location.x/self.world.tile_size)
        self.tile_location_y = int(self.location.y/self.world.tile_size)

        self.speed = 0.

        self.land_based = True
        self.base_speed = self.speed
        
        # Resource attributes
        self.food = 70
        self.water = 70
        self.energy = 70
        # Entity state and functionality
        self.active_info = False
        self.consume_func = consume_func
        # self.consume_func(self)

        self.brain = StateMachine()

        self.id = 0  # Entity ID

        self.tp = 1.0  # Time step or progression
        self.path = []  # Pathfinding nodes
        self.next_node = None  # Next node in path

        # UI elements for displaying entity information
        self.info_bar = pygame.image.load("Images/Entities/info_bar.png").convert()
        self.info_bar.set_colorkey((255, 0, 255))
        self.f_high = (50, 200, 50)
        self.f_low = (255, 0, 0)
        self.w_high = (0, 0, 255)
        self.w_low = (76, 70, 50)
        self.e_high = (0, 255, 0)
        self.e_low = (50, 50, 0)

    def render(self, surface):
        """
        Renders the entity on the game surface.

        Args:
            surface (pygame.Surface): The surface to draw the entity on.
        """
        x, y = self.world_location
        w, h = self.image.get_size()
        pos = (x - (w / 2), y - (h / 2))
        surface.blit(self.image, pos)

    def check_speed(self):
        """
        Checks and adjusts the entity's speed based on the tile type it is currently on.
        """
        if TileFuncs.get_tile(self.world, self.location).name in ["AndrewSmoothStone", "MinecraftSnow"]:
            self.speed = 0.5 * self.base_speed
        else:
            self.speed = self.base_speed
        if DEBUG:
            pass
            # print("Entity ID :" + str(self.id) + ", speed: " + str(self.speed))

    def render_info_bar(self, surface, entity):
        """
        Renders the entity's information bar on the surface, showing food, water, and energy levels.

        Args:
            surface (pygame.Surface): The surface to draw the info bar on.
            entity (GameEntity): The entity whose info bar is being rendered.
        """
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

        # Display the current active state for debugging purposes
        debug_font = pygame.font.SysFont(None, 16)
        debug_ent_active_state_string = "State: " + str(entity.brain.active_state.name)
        ent_active_state_surface = debug_font.render(debug_ent_active_state_string, True, (255, 255, 255))
        surface.blit(ent_active_state_surface, (entity.world_location.x + 10, entity.world_location.y + 15))

    def lerp(self, v1, v2, t):
        """
        Linearly interpolates between two values.

        Args:
            v1 (float): The start value.
            v2 (float): The end value.
            t (float): The interpolation factor (0 to 1).

        Returns:
            float: The interpolated value.
        """
        return (1 - t) * v2 + t * v1

    def process(self, time_passed):
        """
        Processes the entity's logic, including movement and state transitions.

        Args:
            time_passed (float): The time passed since the last update.
        """
        self.brain.think()
        self.world_location = self.location + self.world.world_position

        self.check_speed()

        # if movable
        if self.speed > 0.:
            # if the entity is not at the destination
            c_t = TileFuncs.get_tile(self.world, self.location)
            d_t = TileFuncs.get_tile(self.world, self.destination)
            dist = (c_t.location - d_t.location).get_length()
            if c_t != d_t or dist > 1.0:
                if len(self.path) == 0:
                    # fill path with nodes
                    self.path = a_star_search_nx(self.world.graph, self.location, self.destination) 
                else: 
                    if self.next_node is None:
                        self.next_node = self.path.pop(0)
                    
                    curr_tile = TileFuncs.get_tile(self.world, self.location)
                    next_tile = TileFuncs.get_tile(self.world, self.next_node) 
                    if curr_tile != next_tile:
                        next_node_offset = self.next_node + Vector2(0.1, 0.1) 
                        vec_to_destination = next_node_offset - self.location
                        distance_to_destination = vec_to_destination.get_length()
                        heading = vec_to_destination.get_normalized()
                        travel_distance = min(distance_to_destination, self.speed)
                        self.location += travel_distance * heading * self.speed
                    else:
                        if len(self.path) > 0: 
                            self.next_node = self.path.pop(0) 
                        
            else:
                self.next_node = None
                if self.location != self.destination:
                    vec_to_destination = self.destination - self.location
                    distance_to_destination = vec_to_destination.get_length()
                    heading = vec_to_destination.get_normalized()
                    travel_distance = min(distance_to_destination, self.speed)
                    self.location += travel_distance * heading * self.speed                

        self.tile_location_x = int(self.location.x/self.world.tile_size)
        self.tile_location_y = int(self.location.y/self.world.tile_size)

    def death(self):
        """
        Removes the entity from the world upon death.
        """
        self.world.delete_entity(self)

