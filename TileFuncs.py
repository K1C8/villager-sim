"""
CS5150 Game AI Final Project
Team Member: Jianyan Chen, Ruidi Huang, Xin Qi
Aug 2024

This program contains functions related to Tiles.
"""
from gametools import vector2
import Tile
import math
from gametools.vector2 import Vector2


def get_tile(world, location):
    """
    Retrieves the tile at the given location in the world.

    Args:
        world: The game world instance containing the tiles.
        location (Vector2): The location to retrieve the tile from.

    Returns:
        Tile: The tile at the specified location or a default "Sand" tile if out of bounds.
    """
    tile = get_tile_pos(world, location)
    try:
        return world.tile_array[int(tile.y)][int(tile.x)]
    except IndexError:
        return Tile.Tile(world, "Sand")

def get_tile_neighbours(world, location):
    """
    Retrieves the neighboring tiles around a given location in the world.

    Args:
        world: The game world instance containing the tiles.
        location (Vector2): The location to find neighbors for.

    Returns:
        list: A list of neighboring locations (as Vector2 objects).
    """
    directions = [
        Vector2(1, 0),  # East
        Vector2(-1, 0), # West
        Vector2(0, 1),  # South
        Vector2(0, -1), # North
        Vector2(1, 1),  # Southeast
        Vector2(1, -1), # Northeast
        Vector2(-1, 1), # Southwest
        Vector2(-1, -1) # Northwest
        ]
    neighbors = []
    for direction in directions:
        neighbor_location = location + direction
        tile = get_tile(world, neighbor_location)
        if tile:
            neighbors.append(neighbor_location)
    return neighbors

def get_tile_pos(world, location):
    """
    Converts a location in the world to a tile grid position.

    Args:
        world: The game world instance containing the tiles.
        location (Vector2): The location to convert.

    Returns:
        Vector2: The tile position corresponding to the given location.
    """
    return vector2.Vector2(int(location.x) >> 5, int(location.y) >> 5)

def get_entity(world,location, radius = 20):
    """
    Retrieves an entity within a specified radius of a location in the world.

    Args:
        world: The game world instance containing the entities.
        location (Vector2): The location to search around.
        radius (int, optional): The radius to search within. Defaults to 20.

    Returns:
        tuple: The entity found within the radius, or None if no entity is found.
    """
    for i in world.entities.items():
        ent_location = i[1].world_location
        if ((ent_location.x - location.x)**2 + (ent_location.y - location.y)**2) < radius**2:
            return i
    # print "no ents"

def get_tile_array(world, start_pos, dimensions):
    """
    Retrieves a 2D array of tiles starting from a given position.

    Args:
        world: The game world instance containing the tiles.
        start_pos (Vector2): The starting position to retrieve tiles.
        dimensions (tuple): The dimensions (width, height) of the tile array.

    Returns:
        list: A 2D array of tiles.
    """
    dimensions = (int(dimensions[0]), int(dimensions[1]))

    start_tile = get_tile_pos(world,start_pos)

    array = [[None for i in xrange((dimensions[0] * 2) + 1)]
             for a in xrange((dimensions[1] * 2) + 1)]

    for i in xrange((dimensions[0] * 2) + 1):
        for a in xrange((dimensions[1] * 2) + 1):
            if start_tile.x + i < 0 or start_tile.y + a < 0:
                continue

            else:
                try:
                    array[a][i] = world.tile_array[int((start_tile.y + a) - 1)][int((start_tile.x + i) - 1)]
                except IndexError:
                    #print a, i, start_tile
                    raise IndexError
    return array

def get_vnn_array(world, location, r):
    """
    Returns the Von Neumann neighborhood of a location based on a specified range.

    Args:
        world: The game world instance containing the tiles.
        location (Vector2): The location to get the neighborhood for.
        r (int): The range of the neighborhood.

    Returns:
        list: A list of locations (as Vector2 objects) in the Von Neumann neighborhood.
    """
    """ Stands for Von Neumann Neighborhood.
        Simply returns a neighborhood of locations based
        on the initial location and range r"""

    return_array = []

    """
    range: 3
    num rows: 5 (number of rows is equal to (2 * r) - 1
    0     *      1     left column is row_number
    1   * * *    3     right column is num_in_row
    2 * * * * *  5
    3   * * *    3     middle is illustration of what is looks like
    4     *      1     num_in_row is just how many spots are looked at in the current row.
    """

    for row_number in range((2 * r) - 1):
        if row_number >= r:
            num_in_row = (2 * row_number) - (4 * (row_number - r + 1) - 1)
        else:
            num_in_row = (2 * row_number) + 1

        for cell in range(num_in_row):

            """
            the y_offset goes from -(r - 1) to +(r - 1) (not affected by the inner loop)

            the x_offset goes from -math.floor(num_in_row / 2.0) to +math.floor(num_in_row / 2.0)

            0     0     1 |                  (0, -2)                  x, y offset pairs of a range 3 vnn array
            1   0 1 2   3 |         (-1, -1) (0, -1) (1, -1)
            2 0 1 2 3 4 5 | (-2, 0) (-1, 0 ) (0, 0 ) (1, 0 ) (2, 0)   left column is row_number
            3   0 1 2   3 |         (-1, 1 ) (0, 1 ) (1, 1 )          right column is num_in_row
            4     0     1 |                  (0, 2 )                  middle is cell number
            """

            tile_size = world.tile_size
            x_offset = cell - math.floor(num_in_row / 2.0)
            y_offset = row_number - (r - 1)

            new_location = vector2.Vector2(location.x + (x_offset * tile_size), location.y + (y_offset * tile_size))
            return_array.append(new_location)

    return return_array


def is_entity_collided(world, entity):
    """
    Checks if the given entity has collided with any other entities in the world.

    Args:
        world: The game world instance containing the entities.
        entity: The entity to check for collisions.

    Returns:
        bool: True if a collision is detected, False otherwise.
    """
    for i in world.entities.items():
        if i[1] is not None and i[1].id != entity.id:
            i_tile_location = vector2.Vector2(i[1].tile_location_x, i[1].tile_location_y)
            ent_tile_location = vector2.Vector2(entity.tile_location_x, entity.tile_location_y)
            if i_tile_location == ent_tile_location:
                return True


