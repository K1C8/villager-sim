import random
import math

from configuration.world_configuration import FPS, DAY_DURATION
from gametools.vector2 import Vector2
import TileFuncs

DEBUG = False


def random_dest(entity, recurse=False, r_num=0, r_max=6):
    # Function for going to a random destination
    if recurse:
        entity.orientation += 30
    else:
        entity.orientation += random.randint(-30, 30)
    angle = math.radians(entity.orientation)
    distance = random.randint(50, 100)
    possible_dest = Vector2(entity.location.x + math.cos(angle) * distance,
                            entity.location.y + math.sin(angle) * distance)

    max_distance = entity.speed * FPS * 0.9 * 0.5 * DAY_DURATION
    nearest_food_court = entity.world.get_food_court(entity)
    if nearest_food_court is not None:
        home_distance = possible_dest.get_distance_to(nearest_food_court)
        if home_distance > max_distance:
            print("Entity id " + str(entity.id) + " has reached too far away.")
            possible_dest = nearest_food_court

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
        random_dest(entity, True, r_num+1, r_max)
        return

    else:
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
    world = entity.world
    if len(world.rest_places) < 1:
        return None

    rest_candidates = []
    for rest in world.rest_places:
        rest_candidates.append((rest, rest.get_distance_to(p=entity.location)))
    rest_candidates = sorted(rest_candidates, key=lambda r: r[1])
    if len(rest_candidates) > 0:
        return rest_candidates[0][0]


# def apply_to_sow(entity):
#     world = entity.world
#     if len(world.fields_waiting_to_sow) < 1:
#         return None
#
#     sow_candidates = []
#     for field in sow_candidates:
#         sow_candidates.append((field, field.get_distance_to(p=entity.location)))
#     sow_candidates = sorted(sow_candidates, key=lambda f: f[1])
#     if len(sow_candidates) > 0:
#         world.fields_waiting_to_sow.remove(sow_candidates[0])
#         return sow_candidates[0][0]


