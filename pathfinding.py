"""
A* pathfinding on a 2D grid.

The open set is managed as a min-heap keyed by f = g + h.
Heuristic: Euclidean distance (admissible for 8-directional movement).
Diagonal moves are allowed only when neither adjacent cardinal cell is a wall
(prevents clipping through wall corners).
"""

import heapq
import math


def heuristic(a, b):
    """Euclidean distance – admissible for 8-directional grids."""
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


def astar(grid, start, end):
    """
    Find the shortest path from start to end on grid.

    Parameters
    ----------
    grid  : list[list[int]]  0 = walkable, 1 = wall
    start : (row, col)
    end   : (row, col)

    Returns
    -------
    list[(row, col)] – waypoints from the cell AFTER start up to end,
                       or [] if no path exists.
    """
    rows = len(grid)
    cols = len(grid[0])

    if start == end:
        return []

    # (f_score, tie-break counter, node)
    counter = 0
    open_heap = [(heuristic(start, end), counter, start)]
    open_set  = {start}

    came_from = {}
    g_score   = {start: 0.0}

    # 8-directional neighbour offsets
    DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1),
                  (-1,-1), (-1, 1), (1,-1), (1, 1)]

    while open_heap:
        _, _, current = heapq.heappop(open_heap)

        if current not in open_set:
            continue          # stale entry – already expanded
        open_set.discard(current)

        if current == end:
            # Reconstruct path (exclude the start node itself)
            path = []
            node = current
            while node in came_from:
                path.append(node)
                node = came_from[node]
            path.reverse()
            return path

        r, c = current
        for dr, dc in DIRECTIONS:
            nr, nc = r + dr, c + dc

            if not (0 <= nr < rows and 0 <= nc < cols):
                continue
            if grid[nr][nc] == 1:
                continue

            # Diagonal corner-cut prevention
            if dr != 0 and dc != 0:
                if grid[r][nc] == 1 or grid[nr][c] == 1:
                    continue

            move_cost = 1.414 if (dr != 0 and dc != 0) else 1.0
            new_g = g_score[current] + move_cost
            neighbour = (nr, nc)

            if new_g < g_score.get(neighbour, float('inf')):
                came_from[neighbour] = current
                g_score[neighbour]   = new_g
                f = new_g + heuristic(neighbour, end)
                counter += 1
                heapq.heappush(open_heap, (f, counter, neighbour))
                open_set.add(neighbour)

    return []   # no path found
