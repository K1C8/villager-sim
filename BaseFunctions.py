"""
CS5150 Game AI Final Project
Team Member: Jianyan Chen, Ruidi Huang, Xin Qi
Aug 2024

This program contains base functions for game entities.
"""

import random
import math

from configuration.world_configuration import FPS, DAY_DURATION
from gametools.vector2 import Vector2
import TileFuncs

DEBUG = False


def random_dest(entity, recurse=False, r_num=0, r_max=6):
    """
    Determines a random destination for an entity within the game world.

    Args:
        entity (GameEntity): The entity for which the destination is being calculated.
        recurse (bool): Whether the function is being called recursively to find a valid destination.
        r_num (int): The current recursion depth.
        r_max (int): The maximum recursion depth to attempt before giving up on finding a valid destination.

    Returns:
        None: The destination is directly assigned to the entity's destination attribute.
    """
    # Function for going to a random destination
    if entity.orientation == 0:
        entity.orientation = random.randint(-180, 170)
    # Adjust orientation based on recursion or random variance
    if recurse:
        entity.orientation += 30
    else:
        entity.orientation += random.randint(-25, 30)
    # Calculate the new destination based on the orientation and a random distance
    angle = math.radians(entity.orientation)
    distance = random.randint(50, 100)
    possible_dest = Vector2(entity.location.x + math.cos(angle) * distance,
                            entity.location.y + math.sin(angle) * distance)

    # Calculate maximum allowable distance from the nearest food court
    max_distance = entity.speed * FPS * 0.75 * 0.5 * DAY_DURATION
    nearest_food_court = entity.world.get_food_court(entity)
    if nearest_food_court is not None:
        home_distance = possible_dest.get_distance_to(nearest_food_court)
        if home_distance > max_distance:
            print("Entity id " + str(entity.id) + " has reached too far away.")
            possible_dest = nearest_food_court
            entity.orientation *= -1

    # If the destination will go off the map, it is NOT a valid move under any circumstances.
    bad_spot = False
    if 0 > possible_dest.x > entity.world.world_size[0] or 0 > possible_dest.y > entity.world.world_size[1]:
        bad_spot = True

    if bad_spot:
        if DEBUG:
            "BAD SPOT IS TRUE"

    walk = TileFuncs.get_tile(entity.world, possible_dest).walkable == entity.land_based
    depth_max = r_num >= r_max

    if (not walk and not depth_max) or bad_spot:
        # If the destination is not valid, recurse with incremented depth
        random_dest(entity, True, r_num+1, r_max)
        return

    else:
        # Assign the valid destination to the entity
        entity.destination = possible_dest

    if DEBUG:
        print("Current Tile: " + TileFuncs.get_tile(entity.world, entity.location).__class__.__name__)
        print("Destination Tile: " + TileFuncs.get_tile(entity.world, entity.destination).__class__.__name__)
        print("r_num: %d" % r_num)
        print("walk: ", walk)
        print("")
        if bad_spot:
            print("BAD SPOT, WTF")


def get_idle_destination(entity):
    """
    Finds the nearest idle location (resting place) for an entity within the game world.

    Args:
        entity (GameEntity): The entity for which the idle destination is being calculated.

    Returns:
        Vector2: The location of the nearest rest place, or None if no rest places are available.
    """
    world = entity.world
    # Return None if no resting places are available
    if len(world.rest_places) < 1:
        return None

    # Create a list of rest places sorted by distance from the entity
    rest_candidates = []
    for rest in world.rest_places:
        rest_candidates.append((rest, rest.get_distance_to(p=entity.location)))
    rest_candidates = sorted(rest_candidates, key=lambda r: r[1])
    # Return the closest rest place if available
    if len(rest_candidates) > 0:
        return rest_candidates[0][0]
