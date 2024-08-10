import heapq
import TileFuncs
import Tile
from gametools.vector2 import Vector2

def heuristic(a, b):
    return abs(b.x - a.x) + abs(b.y - a.y)  # Manhattan distance heuristic

def a_star_search(start, goal, world):
    start_key = (start.x, start.y)
    goal_key = (goal.x, goal.y)

    open_heap = []
    heapq.heappush(open_heap, (0, start_key))
    came_from = {start_key: None}
    cost_so_far = {start_key: 0}

    while len(open_heap) > 0:
        current_key = heapq.heappop(open_heap)[1]

        if current_key == goal_key:
            return reconstruct_path(came_from, start_key, goal_key)

        current = Vector2(current_key[0], current_key[1])  # Convert back to Vector2 for neighbor calculations
        print(f"Current Node: {current_key}, Cost So Far: {cost_so_far[current_key]}")
        for next in TileFuncs.get_tile_neighbours(world, current):
            print(f"Checking neighbor: {next}")
            next_key = (int(next.x), int(next.y))
            new_cost = cost_so_far[current_key] + TileFuncs.get_tile(world, next).cost
            print(f"Neighbor {next_key} with new cost {new_cost}")
            if next_key not in cost_so_far or new_cost < cost_so_far[next_key]:
                cost_so_far[next_key] = new_cost
                priority = new_cost + heuristic(goal, next)
                heapq.heappush(open_heap, (priority, next_key))
                came_from[next_key] = current_key

    return []

def reconstruct_path(came_from, start, goal):
    current_key = goal
    path = []
    while current_key != start:
        path.append(Vector2(current_key[0], current_key[1]))  # Convert keys back to Vector2
        current_key = came_from[current_key]
    path.reverse()
    return path