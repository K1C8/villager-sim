"""
CS5150 Game AI Final Project
Team Member: Jianyan Chen, Ruidi Huang, Xin Qi
Aug 2024

This program defines the Angler class for villagers in the game.
Angler performs fishting tasks in the game.
"""

from aitools.StateMachine import *
from Entities import *
from GameEntity import *
from common_state.Feeding import Feeding
from common_state.Idle import Idle
from configuration.villager_configuration import WORKING_TIME_END, ANGLER_RETURN_PROBABILITY
from gametools.vector2 import Vector2
from gametools.ImageFuncs import *
from gametools.ani import *
import BaseFunctions
import TileFuncs
from World import *
from async_funcs.entity_consumption import consume_func_villager


class Angler(GameEntity):
    """
    Angler is a specialized GameEntity that performs fishing tasks in the game.
    The Angler has states such as Fishing, Searching, Delivering, Feeding, and Idle.
    """
    def __init__(self, world, image_string):
        """
        Initializes an Angler entity in the game world.

        Args:
            world (World): The game world in which the Angler exists.
            image_string (str): The path to the image representing the Angler.
        """
        # Initializing the class
        GameEntity.__init__(self, world, "Angler", "Entities/"+image_string, consume_func_villager)

        # Creating the states
        fishing_state = Fishing(self)
        exploring_state = Searching(self)
        delivering_state = Delivering(self)
        feeding_state = Feeding(self)
        idle_state = Idle(self)

        # Adding states to the brain
        self.brain.add_state(fishing_state)
        self.brain.add_state(exploring_state)
        self.brain.add_state(delivering_state)
        self.brain.add_state(feeding_state)
        self.brain.add_state(idle_state)

        self.max_speed = 80.0 * (1.0 / 60.0)
        self.speed = self.max_speed
        self.base_speed = self.speed
        self.view_range = 3
        self.fish = 0
        self.hunger_limit = 40

        self.worldSize = world.world_size
        self.TileSize = self.world.tile_size
        self.primary_state = "Searching"

        # animation variables
        self.animation = Ani(9, 10)
        self.pic = pygame.image.load("Images/Entities/map.png")
        self.img_func = ImageFuncs(18, 17,self.pic)
        self.sprites = self.img_func.get_images(9,0,2)
        self.hit = 0
        self.update()

    def update(self):
        """Updates the Angler's current image based on the animation state."""
        self.image = self.sprites[self.animation.get_frame()]
        self.image.set_colorkey((255,0,255))
        if self.animation.finished:
            self.hit += 1
            self.animation.finished = False


class Fishing(State):
    """
    Fishing is a state where the Angler fishes at a designated location until it has caught enough fish.
    """
    def __init__(self, angler):
        """
        Initializes the Fishing state.

        Args:
            angler (Angler): The Angler entity associated with this state.
        """
        State.__init__(self, "Fishing")
        self.angler = angler

    def check_conditions(self):
        """
        Checks if the conditions to continue fishing or transition to another state are met.

        Returns:
            str: The next state to transition to, if any.
        """
        # Check if Angler has reached its destination
        if self.angler.location.get_distance_to(self.angler.destination) <= 0.25 * self.angler.world.tile_size:
            self.angler.destination = Vector2(self.angler.location)
            self.angler.update()

        # Transition to Delivering state if enough fish are caught
        if self.angler.fish >= 1:
            return "Delivering"

    def do_actions(self):
        """Performs actions associated with fishing."""
        if self.angler.location == self.angler.destination and self.angler.hit >= 4:
            # TODO: Why is this checking if the tile is fishable if it has been fishing there?
            
            # for tile_location in TileFuncs.get_vnn_array(self.angler.world, self.angler.location, 2):
            #     if TileFuncs.get_tile(self.angler.world, tile_location).fishable:
            #         self.angler.hit = 0
            #         self.angler.fish = 1
            self.angler.fish = randint(5, 10)
            self.angler.hit = 0

    def entry_actions(self):
        """Defines actions to be taken when entering the Fishing state."""
        BaseFunctions.random_dest(self.angler)


class Searching(State):
    """
    Searching is a state where the Angler searches for a suitable fishing spot.
    """
    def __init__(self, angler):
        """
        Initializes the Searching state.

        Args:
            angler (Angler): The Angler entity associated with this state.
        """
        State.__init__(self, "Searching")
        self.angler = angler

    def entry_actions(self):
        """Defines actions to be taken when entering the Searching state."""
        dice = random()
        if dice > ANGLER_RETURN_PROBABILITY or len(self.angler.world.known_fishing_spots) == 0:
            BaseFunctions.random_dest(self.angler)
        else:
            known_spots = self.angler.world.known_fishing_spots
            spot_dice = randint(1, len(known_spots)) - 1
            self.angler.destination = known_spots[spot_dice]

    def do_actions(self):
        pass

    def check_conditions(self):
        """
        Checks if the conditions to continue searching or transition to another state are met.

        Returns:
            str: The next state to transition to, if any.
        """
        # Check if the Angler has reached its destination
        if self.angler.location.get_distance_to(self.angler.destination) < 0.25 * self.angler.world.tile_size:
            location_array = TileFuncs.get_vnn_array(self.angler.world,(self.angler.location), self.angler.view_range)

            for location in location_array:
                # TODO: This will make the angler go into the water, change this to go to the nearest walkable tile.
                test_tile = TileFuncs.get_tile(self.angler.world, location)
                if test_tile.fishable:
                    destination_array = TileFuncs.get_vnn_array(world=self.angler.world, location=location, r=2)
                    for destination in destination_array:
                        destination_tile = TileFuncs.get_tile(self.angler.world, destination)
                        if destination_tile.walkable:
                            self.angler.destination = destination.copy()
                            self.angler.destination.x = int(self.angler.destination.x // 32 * 32)
                            self.angler.destination.y = int(self.angler.destination.y // 32 * 32)
                            if self.angler.destination not in self.angler.world.known_fishing_spots:
                                print("Angler ID: " + str(self.angler.id) + " adding new fishing spots: "
                                      + str(self.angler.destination))
                                self.angler.world.known_fishing_spots.append(self.angler.destination)
                            return "Fishing"

            BaseFunctions.random_dest(self.angler)

        # Check if Angler needs to eat
        if self.angler.food < self.angler.hunger_limit:
            return "Feeding"
        # Bro you have to work and get something before going home!
        # if self.angler.world.time >= WORKING_TIME_END:
        #     return "Idle"

    def exit_actions(self):
        pass


class Delivering(State):
    """
    Delivering is a state where the Angler delivers the caught fish to a designated location.
    """
    def __init__(self, angler):
        """
        Initializes the Delivering state.

        Args:
            angler (Angler): The Angler entity associated with this state.
        """
        State.__init__(self, "Delivering")
        self.angler = angler

    def entry_actions(self):
        """Defines actions to be taken when entering the Delivering state."""
        self.angler.destination = copy.deepcopy(self.angler.world.get_fish_market(self.angler))

    def do_actions(self):
        pass

    def check_conditions(self):
        """
        Checks if the conditions to continue delivering or transition to another state are met.

        Returns:
            str: The next state to transition to, if any.
        """
        # Check if Angler has reached the delivery point
        if self.angler.location.get_distance_to(self.angler.destination) < 15:
            self.angler.world.fish += self.angler.fish
            self.angler.fish = 0
            return "Feeding"

    def exit_actions(self):
        pass
