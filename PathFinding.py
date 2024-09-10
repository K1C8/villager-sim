"""
CS5150 Game AI Final Project
Team Member: Jianyan Chen, Ruidi Huang, Xin Qi
Aug 2024

This program contains functions for A star path finding for villagers.
"""

import heapq
import TileFuncs
import Tile
from gametools import vector2
import networkx as nx


def create_graph(world):
    """
    Creates a graph representation of the game world using the NetworkX library.
    Each tile in the world is treated as a node, and edges are created between neighboring tiles.

    Args:
        world: The game world containing tiles with various properties like cost.

    Returns:
        networkx.Graph: A graph where nodes represent tiles in the world and edges represent possible movements 
                        between tiles with weights based on movement cost.
    """
    G = nx.Graph()
    # print("create graph")
    for x in range(world.w // 32):
        for y in range(world.h // 32):
            node = (x, y)  # Create a node for each tile based on its grid coordinates
            node_vec = vector2.Vector2(x, y) * 32  # Convert grid coordinates to world coordinates
            tile = TileFuncs.get_tile(world, node_vec)  # Retrieve the tile at the given coordinates
            if tile:
                G.add_node(node)
                # Check all 8 neighboring tiles (including diagonals)
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:  # 4-directions in W, S, N, and E
                    neighbor = (x + dx, y + dy)
                    neighbor_vec = vector2.Vector2(x + dx, y + dy) * 32
                    neighbor_tile = TileFuncs.get_tile(world, neighbor_vec)
                    if neighbor_tile:
                        # Add an edge between the current node and the neighboring node with a weight based on the
                        # neighbor's cost
                        G.add_edge(node, neighbor, weight=0.5 * neighbor_tile.cost + 0.5 * tile.cost)
                for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:  # 4-directions in NW, SW, NE, and SE
                    neighbor = (x + dx, y + dy)
                    neighbor_vec = vector2.Vector2(x + dx, y + dy) * 32
                    neighbor_tile = TileFuncs.get_tile(world, neighbor_vec)
                    if neighbor_tile:
                        # Add an edge between the current node and the neighboring node with a weight based on the
                        # neighbor's cost
                        G.add_edge(node, neighbor, weight=0.707 * neighbor_tile.cost + 0.707 * tile.cost)
    return G


def heuristic(a, b):
    """
    Heuristic function used in the A* algorithm to estimate the cost of the cheapest path from node 'a' to node 'b'.
    This implementation uses the Manhattan distance, suitable for grid-based movement.

    Args:
        a (tuple): The coordinates of the first node (x1, y1).
        b (tuple): The coordinates of the second node (x2, y2).

    Returns:
        int: The Manhattan distance between nodes 'a' and 'b'.
    """
    (x1, y1) = a
    (x2, y2) = b
    return abs(x1 - x2) + abs(y1 - y2)


def a_star_search_nx(graph, start, goal):
    """
    Performs A* search on the given graph to find the shortest path from 'start' to 'goal'.

    Args:
        graph (networkx.Graph): The graph representing the world, with nodes as tiles and edges as movements.
        start (vector2.Vector2): The starting position in world coordinates.
        goal (vector2.Vector2): The goal position in world coordinates.

    Returns:
        list of vector2.Vector2: The path from start to goal as a list of world coordinates.
    """
    # Convert start and goal positions from world coordinates to grid coordinates
    start_node = (int(start.x // 32), int(start.y // 32))
    goal_node = (int(goal.x // 32), int(goal.y // 32))
    path = nx.astar_path(graph, start_node, goal_node, heuristic=heuristic, weight='weight')
    # Remove the first node (start node) to return the path after the start point
    path.pop(0)
    # Convert the path from grid coordinates back to world coordinates
    return [vector2.Vector2(p[0], p[1]) * 32 + vector2.Vector2(16, 16) for p in path]
