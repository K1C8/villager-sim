"""
CS5150 Game AI Final Project
Team Member: Jianyan Chen, Ruidi Huang, Xin Qi
Aug 2024
This program contains all functions for making building decisions for builders. 
"""

import queue
import Buildings
from configuration.world_configuration import UTILIZE_LIMIT
from gametools import vector2

DEBUG = True

def building_decision(world):
    """
    Determines the next building to construct in the world based on resource utilization.

    Args:
        world: The current state of the game world, containing information about resources,
               buildings, and population.

    Returns:
        dict or None: A dictionary containing the class of the building to be constructed 
                      and its location. If no building decision is made, returns None.
    """
    next_building = None
    # Decide which building to build next based on resource utilization limits
    if float(world.living_entities_count) / float(world.MAXpopulation) >= UTILIZE_LIMIT:
        next_building = {"class": Buildings.Manor, "location": None}
    elif float(world.fish) / float(world.MAXFish) >= UTILIZE_LIMIT:
        next_building = {"class": Buildings.FishMarket, "location": None}
    elif float(world.stone) / float(world.MAXStone) >= UTILIZE_LIMIT:
        next_building = {"class": Buildings.Stonework, "location": None}
    elif float(world.crop) / float(world.MAXCrop) >= UTILIZE_LIMIT:
        next_building = {"class": Buildings.Barn, "location": None}
    elif float(world.wood) / float(world.MAXWood) >= UTILIZE_LIMIT:
        next_building = {"class": Buildings.LumberYard, "location": None}


    # Determine if a new building can be added based on the current number of builders.
    if next_building is not None and len(world.building_list) < world.builder_count:
        if DEBUG:
            print("New building decision triggered.")
        
        # Get the size of the building
        size_x = next_building["class"].SIZE_X
        size_y = next_building["class"].SIZE_Y
        
        # Initialize variables for location search
        is_location_get = False
        village_loc_tile = world.village_location_tile
        deviation_radius = 0
        candidates_queue = get_queue(deviation_radius, village_loc_tile, world)
        grid = candidates_queue.get()
        if DEBUG:
            print("Checking grid: " + str(grid))
        
        # Attempt to find a suitable location for the building
        while not is_location_get:
            if grid is None:
                return None
            location = world.get_next_building_pos(grid, size_x, size_y)
            
            # Check if the location is already occupied by another waiting building
            if location is not None:
                for waiting_bldg in world.building_list:
                    if waiting_bldg["location"].get_distance_to(location) < 1:
                        location = None
                        break
            
            # If a valid location is found, return the building decision
            if location is not None:
                is_location_get = True
                next_building["location"] = location
                return next_building
            else:
                # Expand the search radius if no suitable location is found
                if candidates_queue.empty():
                    deviation_radius += 1
                    candidates_queue = get_queue(deviation_radius, village_loc_tile, world)
                grid = candidates_queue.get()
    else:
        return None


def get_queue(radius, center, world):
    """
    Generates a queue of candidate grid locations around the village center 
    for potential building placement.

    Args:
        radius (int): The current radius of deviation from the village center.
        center (Vector2): The center point of the village in tile coordinates.
        world: The current state of the game world, containing information about dimensions.

    Returns:
        queue.Queue: A queue containing vector2.Vector2 objects representing candidate locations.
    """
    grid_size = 8 # Size of each grid in the world
    limit_x = world.w // 32 # Maximum x-coordinate for the grid
    limit_y = world.h // 32 # Maximum y-coordinate for the grid
    candidates = [] # List to store candidate locations

    # Generate candidates by expanding outward from the center in the x-direction
    for x in range(-radius, radius+1):
        curr_loc_x = center.x + grid_size * x
        curr_loc_y = center.y
        if 0 <= curr_loc_x < limit_x and 0 <= curr_loc_y < limit_y:
            candidates.append(vector2.Vector2(curr_loc_x, curr_loc_y + radius * grid_size))
            candidates.append(vector2.Vector2(curr_loc_x, curr_loc_y - radius * grid_size))

    # Generate candidates by expanding outward from the center in the y-direction
    for y in range(-radius + 1, radius):
        curr_loc_x = center.x
        curr_loc_y = center.y + grid_size * y
        if 0 <= curr_loc_x < limit_x and 0 <= curr_loc_y < limit_y:
            candidates.append(vector2.Vector2(curr_loc_x + radius * grid_size, curr_loc_y))
            candidates.append(vector2.Vector2(curr_loc_x - radius * grid_size, curr_loc_y))
    if len(candidates) > 0:
        if DEBUG:
            print(candidates)

    # Convert the list of candidates to a queue for sequential processing
    candidates_queue = queue.Queue()
    for cand in candidates:
        candidates_queue.put(cand)
    return candidates_queue
