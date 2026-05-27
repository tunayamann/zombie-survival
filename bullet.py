"""
Bullet with object-pool backing.

BulletPool pre-allocates BULLET_POOL_SIZE Bullet instances at startup.
When a bullet is needed, an inactive one is reused instead of allocating,
which prevents garbage-collection pauses during gameplay.
"""

import pygame

from settings import (BULLET_COLOR, BULLET_POOL_SIZE, BULLET_RADIUS,
                      BULLET_SPEED, SCREEN_HEIGHT, SCREEN_WIDTH, UI_HEIGHT)
from tile_map import world_to_grid


class Bullet:
    def __init__(self):
        self.x = self.y = 0.0
        self.vx = self.vy = 0.0
        self.active   = False
        self.radius   = BULLET_RADIUS
        self.damage   = 25
        self._age     = 0.0
        self._maxage  = 2.2      # seconds before auto-expire

    def activate(self, x: float, y: float, dx: float, dy: float):
        self.x, self.y = x, y
        self.vx = dx * BULLET_SPEED
        self.vy = dy * BULLET_SPEED
        self.active = True
        self._age   = 0.0

    def deactivate(self):
        self.active = False

    def update(self, dt: float, grid):
        if not self.active:
            return

        self._age += dt
        if self._age >= self._maxage:
            self.deactivate()
            return

        self.x += self.vx * dt
        self.y += self.vy * dt

        # Out-of-bounds check
        if not (0 < self.x < SCREEN_WIDTH and UI_HEIGHT < self.y < SCREEN_HEIGHT):
            self.deactivate()
            return

        # Wall collision
        row, col = world_to_grid(self.x, self.y)
        if 0 <= row < len(grid) and 0 <= col < len(grid[0]):
            if grid[row][col] == 1:
                self.deactivate()

    def draw(self, surface: pygame.Surface):
        if self.active:
            pygame.draw.circle(surface, BULLET_COLOR,
                               (int(self.x), int(self.y)), self.radius)


class BulletPool:
    """Fixed-size object pool – avoids per-frame allocation."""

    def __init__(self, size: int = BULLET_POOL_SIZE):
        self._pool = [Bullet() for _ in range(size)]

    def get(self) -> Bullet | None:
        for b in self._pool:
            if not b.active:
                return b
        return None   # pool exhausted (shouldn't happen at normal fire rates)

    def active_bullets(self):
        return [b for b in self._pool if b.active]

    def update(self, dt: float, grid):
        for b in self._pool:
            if b.active:
                b.update(dt, grid)

    def draw(self, surface: pygame.Surface):
        for b in self._pool:
            if b.active:
                b.draw(surface)
