import random
import math
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

    # If the destination will go off the map, it is NOT a valid move under any circumstances.
    bad_spot = False
    if 0 > possible_dest.x > entity.world.world_size[0] or 0 > possible_dest.y > entity.world.world_size[1]:
        bad_spot = True
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
