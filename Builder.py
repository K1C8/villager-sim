from aitools.StateMachine import *
from World import *
from GameEntity import *
from async_funcs.entity_consumption import consume_func_villager
from common_state.Feeding import Feeding
from common_state.Idle import Idle
from gametools.ani import Ani
from gametools.vector2 import Vector2

from Buildings import *

from random import *

import pygame


class Builder(GameEntity):
    def __init__(self, world, image):
        GameEntity.__init__(self, world=world, name="Builder", image_string=image, consume_func=consume_func_villager)

        self.current_build = None

        self.speed = 80.0 * (1.0 / 60.0)
        self.primary_state = "Builder_Idle"
        self.hunger_limit = 60

        # Building speed of Builders
        self.tp = 0.05

        self.building_state = Builder_Building(self)
        self.idle_state = Idle(self)
        self.Finding_state = Builder_Finding(self)
        self.feeding_state = Feeding(self)

        self.brain.add_state(self.building_state)
        self.brain.add_state(self.idle_state)
        self.brain.add_state(self.Finding_state)
        self.brain.add_state(self.feeding_state)

        # self.IdleLocation = rest.location.copy()
        self.animation = Ani(6, 10)
        self.pic = pygame.image.load("Images/Entities/map.png")
        self.img_func = ImageFuncs(18, 17, self.pic)
        self.sprites = self.img_func.get_images(5, 0, 4)
        self.hit = 0
        self.update()

    def update(self):
        # Updates image every 10 cycles and adds 1 to the hit count; tilling and harvesting require 4 hits;
        # sowing and watering require 8 hits
        self.image = self.sprites[self.animation.get_frame()]
        self.image.set_colorkey((255, 0, 255))
        if self.animation.finished:
            # print("Farmer id " + str(self.id) + " hit +1.")
            self.hit += 1
            self.animation.finished = False


class Builder_Building(State):
    def __init__(self, Builder):
        State.__init__(self, "Building")
        self.Builder = Builder

    def check_conditions(self):
        if self.building_complete >= 5.0:
            self.Builder.target.create()

            # self.Builder.world.BuildingQueue.remove(self.Builder.target)
            return "Finding"

    def do_actions(self):
        self.building_complete += self.Builder.tp

    def entry_actions(self):
        self.Builder.destination = self.Builder.location.copy()
        self.building_complete = 0.0


class Builder_Finding(State):  # Finding a suitable place to build.
    """If:
    Lumberyard - In the woods not near anything else
    Docks - Edge of the water, decently distanced from others
    House - Somewhere in the town area
    Manor - near top of the map or maybe replaces a house.
    """

    def __init__(self, Builder):
        State.__init__(self, "Finding")
        self.Builder = Builder

    def check_conditions(self):
        if self.Builder.target is None:
            return "Idle"

        if self.Builder.location.get_distance_to(self.Builder.destination) < 2:
            return "Building"

    def do_actions(self):
        pass

    def entry_actions(self):
        try:
            self.Builder.target = None
            self.Builder.target = self.Builder.world.BuildingQueue.get()
            if self.Builder.target is None:
                return
            if (self.Builder.world.wood >= self.Builder.target["class"].COST_WOOD and
                    self.Builder.world.stone >= self.Builder.target["class"].COST_STONE):
                self.Builder.destination = self.Builder.target["location"].copy()
                self.Builder.building_class = self.Builder.target["class"]
            else:
                self.Builder.world.BuildingQueue.put(self.Builder.target)
                self.Builder.target = None

        except IndexError:
            pass


class Builder_Idle(State):
    def __init__(self, Builder):
        State.__init__(self, "Idle")
        self.Builder = Builder

    def entry_actions(self):
        # self.Builder.destination = self.Builder.IdleLocation
        pass

    def check_conditions(self):
        if len(self.Builder.world.BuildingQueue) >= 1:
            return "Finding"

        if self.Builder.food < self.Builder.hunger_limit:
            return "Feeding"
