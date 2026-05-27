"""
Broad-phase collision detection via a uniform spatial hash grid.

Instead of checking every bullet against every enemy (O(b*e)), entities are
bucketed into fixed-size cells and only entities in the same or adjacent cells
are compared – reducing average-case work significantly for sparse scenes.
"""


class SpatialGrid:
    def __init__(self, cell_size=64):
        self.cell_size = cell_size
        self.cells: dict[tuple, list] = {}

    def clear(self):
        self.cells.clear()

    def add(self, entity, x, y):
        key = (int(x // self.cell_size), int(y // self.cell_size))
        self.cells.setdefault(key, []).append(entity)

    def get_nearby(self, x, y):
        """Return all entities in the 3×3 neighbourhood of (x, y)."""
        cx = int(x // self.cell_size)
        cy = int(y // self.cell_size)
        result = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                result.extend(self.cells.get((cx + dx, cy + dy), []))
        return result
