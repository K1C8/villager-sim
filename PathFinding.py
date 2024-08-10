import heapq
import TileFuncs
import Tile
from gametools import vector2
import networkx as nx

def create_graph(world):
    G = nx.Graph()
    print("create graph")
    for x in range(world.w // 32):
        for y in range(world.h // 32):
            node = (x, y)
            print("start with node: ", node)
            node_vec = vector2.Vector2(x, y) * 32
            tile = TileFuncs.get_tile(world, node_vec)
            if tile:
                G.add_node(node)
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:  # 8-directions
                    neighbor = (x + dx, y + dy)
                    neighbor_vec = vector2.Vector2(x + dx, y + dy) * 32
                    neighbor_tile = TileFuncs.get_tile(world, neighbor_vec)
                    if neighbor_tile:
                        G.add_edge(node, neighbor, weight=neighbor_tile.cost)
    return G


def heuristic(a, b):
    (x1, y1) = a
    (x2, y2) = b
    return abs(x1 - x2) + abs(y1 - y2)  # Manhattan distance

def a_star_search_nx(graph, start, goal):
    start_node = (int(start.x // 32), int(start.y // 32))
    goal_node = (int(goal.x // 32), int(goal.y // 32))
    path = nx.astar_path(graph, start_node, goal_node, heuristic=heuristic, weight='weight')
    path.pop(0)
    return [vector2.Vector2(p[0], p[1]) * 32 for p in path]

