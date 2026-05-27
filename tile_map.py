from settings import TILE_SIZE, GRID_ROWS, GRID_COLS, UI_HEIGHT


def create_map():
    """
    Build the level grid.
    0 = walkable floor, 1 = wall.
    Border is always solid; interior obstacles force A* to route around them.
    """
    grid = [[0] * GRID_COLS for _ in range(GRID_ROWS)]

    # Solid border
    for r in range(GRID_ROWS):
        grid[r][0] = 1
        grid[r][GRID_COLS - 1] = 1
    for c in range(GRID_COLS):
        grid[0][c] = 1
        grid[GRID_ROWS - 1][c] = 1

    # Interior wall clusters: (start_row, start_col, height, width)
    obstacles = [
        (2,  4, 5, 2),   # upper-left pillar
        (2, 19, 5, 2),   # upper-right pillar
        (4, 11, 2, 3),   # top-center block
        (8,  9, 3, 2),   # center-left block
        (8, 14, 3, 2),   # center-right block
        (12,  4, 3, 2),  # lower-left pillar
        (12, 19, 3, 2),  # lower-right pillar
    ]

    for (sr, sc, h, w) in obstacles:
        for dr in range(h):
            for dc in range(w):
                r, c = sr + dr, sc + dc
                if 0 < r < GRID_ROWS - 1 and 0 < c < GRID_COLS - 1:
                    grid[r][c] = 1

    return grid


def world_to_grid(x, y):
    """Pixel position → (row, col) clamped to valid range."""
    col = int(x // TILE_SIZE)
    row = int((y - UI_HEIGHT) // TILE_SIZE)
    row = max(0, min(row, GRID_ROWS - 1))
    col = max(0, min(col, GRID_COLS - 1))
    return row, col


def grid_to_world(row, col):
    """Grid (row, col) → pixel center of that tile."""
    x = col * TILE_SIZE + TILE_SIZE // 2
    y = row * TILE_SIZE + TILE_SIZE // 2 + UI_HEIGHT
    return x, y
