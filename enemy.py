import math

import pygame

from pathfinding import astar
from settings import (ENEMY_ATTACK_COOL, ENEMY_ATTACK_RANGE, ENEMY_COLOR,
                      ENEMY_DAMAGE, ENEMY_HEALTH_BASE, ENEMY_PATH_UPDATE,
                      ENEMY_RADIUS, ENEMY_SPEED, GREEN, RED, WHITE)
from tile_map import grid_to_world, world_to_grid


class Enemy:
    def __init__(self):
        self.x = self.y = 0.0
        self.health = self.max_health = 0
        self.speed  = 0.0
        self.active = False
        self.radius = ENEMY_RADIUS

        self._path         = []      # list of (x, y) waypoints from A*
        self._path_timer   = 0.0
        self._attack_cool  = 0.0

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def activate(self, x: float, y: float, wave: int):
        self.x, self.y = x, y
        self.health     = ENEMY_HEALTH_BASE + (wave - 1) * 20
        self.max_health = self.health
        self.speed      = ENEMY_SPEED  + (wave - 1) * 5
        self.active     = True
        self._path      = []
        self._path_timer  = ENEMY_PATH_UPDATE   # force immediate recalc
        self._attack_cool = 0.0

    def deactivate(self):
        self.active = False
        self._path  = []

    # ── Per-frame update ──────────────────────────────────────────────────────

    def update(self, dt: float, grid, player):
        if not self.active:
            return

        # Refresh A* path periodically
        self._path_timer += dt
        if self._path_timer >= ENEMY_PATH_UPDATE:
            self._path_timer = 0.0
            self._refresh_path(grid, player)

        self._follow_path(dt)

        # Melee attack
        if self._attack_cool > 0:
            self._attack_cool -= dt
        dist = math.hypot(self.x - player.x, self.y - player.y)
        if dist <= ENEMY_RADIUS + ENEMY_ATTACK_RANGE and self._attack_cool <= 0:
            player.take_damage(ENEMY_DAMAGE)
            self._attack_cool = ENEMY_ATTACK_COOL

    # ── Pathfinding ───────────────────────────────────────────────────────────

    def _refresh_path(self, grid, player):
        rows, cols = len(grid), len(grid[0])
        start = world_to_grid(self.x,    self.y)
        end   = world_to_grid(player.x,  player.y)

        # Safety checks – don't query A* if start/end is inside a wall
        for r, c in (start, end):
            if not (0 <= r < rows and 0 <= c < cols):
                return
            if grid[r][c] == 1:
                return

        cells = astar(grid, start, end)
        # Convert grid cells to world-space waypoints
        self._path = [grid_to_world(r, c) for r, c in cells]

    # ── Movement along path ───────────────────────────────────────────────────

    def _follow_path(self, dt: float):
        if not self._path:
            return
        tx, ty = self._path[0]
        dx, dy  = tx - self.x, ty - self.y
        dist    = math.hypot(dx, dy)

        if dist < 5:                   # close enough – advance to next waypoint
            self._path.pop(0)
            return

        self.x += (dx / dist) * self.speed * dt
        self.y += (dy / dist) * self.speed * dt

    # ── Combat ────────────────────────────────────────────────────────────────

    def take_damage(self, amount: int) -> bool:
        """Apply damage. Returns True if the enemy died."""
        self.health -= amount
        if self.health <= 0:
            self.health = 0
            self.deactivate()
            return True
        return False

    # ── Drawing ───────────────────────────────────────────────────────────────

    def draw(self, surface: pygame.Surface):
        if not self.active:
            return
        ix, iy = int(self.x), int(self.y)

        # Body
        pygame.draw.circle(surface, ENEMY_COLOR, (ix, iy), self.radius)
        pygame.draw.circle(surface, WHITE,       (ix, iy), self.radius, 2)

        # Red glowing eyes
        pygame.draw.circle(surface, (255,  40,  40), (ix - 5, iy - 4), 3)
        pygame.draw.circle(surface, (255,  40,  40), (ix + 5, iy - 4), 3)

        # Health bar
        bw = self.radius * 2
        bx = ix - self.radius
        by = iy - self.radius - 9
        pygame.draw.rect(surface, RED,   (bx, by, bw, 4))
        pygame.draw.rect(surface, GREEN, (bx, by, int(bw * self.health / self.max_health), 4))
