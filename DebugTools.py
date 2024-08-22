"""
CS5150 Game AI Final Project
Team Member: Jianyan Chen, Ruidi Huang, Xin Qi
Aug 2024

This program contains debug functions.
"""

import TileFuncs

def print_surrounding_tiles(world, print_type="Name"):
    """
    Prints the surrounding tiles of the first entity in the world within a certain range.

    Args:
        world (World): The game world object that contains the entities and tile information.
        print_type (str): The type of information to print. Can be "Name" to print tile names
                          or any other value to print tile coordinates.

    This function uses a 2-tile radius to determine the surrounding tiles of the first entity
    in the world and prints them in a specific format. The output is either the names of the
    tiles or their coordinates, depending on the value of `print_type`.
    """
    tile_range = 2
    location_array = TileFuncs.get_vnn_array(world, world.entities[0].location, tile_range)

    if print_type=="Name":
        tile_list = tile_array_from_location(world, location_array)
    else:
        tile_list = location_array
    # print "Length of tile_list: %d"%len(tile_list)

    print(tile_list[0])
    print(tile_list[1], tile_list[2], tile_list[3])
    print(tile_list[4])
    print("")

def tile_array_from_location(world, array):
    """
    Converts an array of locations into an array of tile names.

    Args:
        world (World): The game world object that contains the tile information.
        array (list): A list of Vector2 objects representing tile locations.

    Returns:
        list: A list of tile names corresponding to the locations in the input array.
    """
    return_array = []
    for i in array:
        return_array.append(TileFuncs.get_tile(world, i).name)

    return return_array

def print_location_tile(world, location):
    """
    Prints the class name of the tile at the specified location.

    Args:
        world (World): The game world object that contains the tile information.
        location (Vector2): The location of the tile to print.

    This function prints the class name of the tile at the given location in the world.
    """
    print(TileFuncs.get_tile(world, location).__class__.__name__)
