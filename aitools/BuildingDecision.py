import queue

import Buildings
from configuration.world_configuration import UTILIZE_LIMIT
from gametools import vector2

DEBUG = True

def building_decision(world):
    next_building = None
    # Decide which building to build next.
    if float(world.living_entities_count) / float(world.MAXpopulation) >= UTILIZE_LIMIT:
        next_building = {"class": Buildings.Manor, "location": None}
    elif float(world.stone) / float(world.MAXStone) >= UTILIZE_LIMIT:
        next_building = {"class": Buildings.Stonework, "location": None}
    elif float(world.crop) / float(world.MAXCrop) >= UTILIZE_LIMIT:
        next_building = {"class": Buildings.Barn, "location": None}
    elif float(world.fish) / float(world.MAXFish) >= UTILIZE_LIMIT:
        next_building = {"class": Buildings.FishMarket, "location": None}

    if next_building is not None and len(world.building_list) < world.builder_count:
        if DEBUG:
            print("New building decision triggered.")
        size_x = next_building["class"].SIZE_X
        size_y = next_building["class"].SIZE_Y
        is_location_get = False
        village_loc_tile = world.village_location_tile
        deviation_radius = 0
        candidates_queue = get_queue(deviation_radius, village_loc_tile, world)
        grid = candidates_queue.get()
        if DEBUG:
            print("Checking grid: " + str(grid))
        while not is_location_get:
            if grid is None:
                return None
            location = world.get_next_building_pos(grid, size_x, size_y)
            if location is not None:
                for waiting_bldg in world.building_list:
                    if waiting_bldg["location"].get_distance_to(location) < 1:
                        location = None
                        break
            if location is not None:
                is_location_get = True
                next_building["location"] = location
                return next_building
            else:
                if candidates_queue.empty():
                    deviation_radius += 1
                    candidates_queue = get_queue(deviation_radius, village_loc_tile, world)
                grid = candidates_queue.get()
    else:
        return None


def get_queue(radius, center, world):
    grid_size = 8
    limit_x = world.w // 32
    limit_y = world.h // 32
    candidates = []
    for x in range(-radius, radius+1):
        curr_loc_x = center.x + grid_size * x
        curr_loc_y = center.y
        if 0 <= curr_loc_x < limit_x and 0 <= curr_loc_y < limit_y:
            candidates.append(vector2.Vector2(curr_loc_x, curr_loc_y + radius * grid_size))
            candidates.append(vector2.Vector2(curr_loc_x, curr_loc_y - radius * grid_size))

    for y in range(-radius+1, radius):
        curr_loc_x = center.x
        curr_loc_y = center.y + grid_size * y
        if 0 <= curr_loc_x < limit_x and 0 <= curr_loc_y < limit_y:
            candidates.append(vector2.Vector2(curr_loc_x + radius * grid_size, curr_loc_y))
            candidates.append(vector2.Vector2(curr_loc_x - radius * grid_size, curr_loc_y))
    if len(candidates) > 0:
        if DEBUG:
            print(candidates)
    candidates_queue = queue.Queue()
    for cand in candidates:
        candidates_queue.put(cand)
    return candidates_queue
