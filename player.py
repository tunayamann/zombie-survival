"""
player.py – Player entity: movement, aiming, shooting, and damage.

Movement uses WASD (or arrow keys) with diagonal normalisation to prevent
the classic diagonal-speed bug.  Wall collision is tested via four AABB probe
points placed at the corners of the player's bounding circle.
"""

import math

import pygame

from settings import (PLAYER_COLOR, PLAYER_HEALTH, PLAYER_RADIUS,
                      PLAYER_SPEED, BULLET_COOLDOWN, RED, WHITE, TILE_SIZE)
from tile_map import world_to_grid


class Player:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.health     = PLAYER_HEALTH
        self.max_health = PLAYER_HEALTH
        self.speed      = PLAYER_SPEED
        self.radius     = PLAYER_RADIUS
        self.alive      = True

        self._angle      = 0.0   # aim direction in degrees (for gun-barrel drawing)
        self._shoot_cool = 0.0   # countdown timer; shooting blocked while > 0
        self._hit_flash  = 0.0   # counts down from 0.15 s after taking damage

    # ── Per-frame update ──────────────────────────────────────────────────────

    def update(self, keys, dt: float, grid):
        self._move(keys, dt, grid)
        if self._shoot_cool > 0:
            self._shoot_cool -= dt
        if self._hit_flash > 0:
            self._hit_flash = max(0.0, self._hit_flash - dt)

    def update_aim(self, mx: int, my: int):
        """Recalculate aim angle from the current mouse cursor position."""
        dx = mx - self.x
        dy = my - self.y
        # atan2 with negated dy because pygame's y-axis points downward
        self._angle = math.degrees(math.atan2(-dy, dx))

    # ── Movement ──────────────────────────────────────────────────────────────

    def _move(self, keys, dt: float, grid):
        dx = dy = 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:    dy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:  dy += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:  dx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx += 1

        # Normalise diagonal movement so speed is consistent in all directions
        if dx != 0 and dy != 0:
            factor = 1 / math.sqrt(2)
            dx *= factor
            dy *= factor

        step = self.speed * dt
        nx, ny = self.x + dx * step, self.y + dy * step

        # Axis-separated collision: attempt X and Y moves independently so the
        # player can slide along a wall rather than stopping dead
        if not self._hits_wall(nx, self.y, grid):
            self.x = nx
        if not self._hits_wall(self.x, ny, grid):
            self.y = ny

    def _hits_wall(self, x: float, y: float, grid) -> bool:
        """
        Test whether the player circle at (x, y) overlaps any wall tile.

        Four probe points are checked at the corners of a square inscribed in
        the collision circle (radius shrunk by 2 px to avoid false positives on
        tile edges).  This AABB approximation is fast and accurate enough for a
        circle of this size.
        """
        r = self.radius - 2
        for px in (x - r, x + r):
            for py in (y - r, y + r):
                row, col = world_to_grid(px, py)
                if 0 <= row < len(grid) and 0 <= col < len(grid[0]):
                    if grid[row][col] == 1:
                        return True
        return False

    # ── Combat ────────────────────────────────────────────────────────────────

    def try_shoot(self, bullet_pool, mx: int, my: int) -> bool:
        """
        Fire one bullet toward (mx, my) if the cooldown has expired.
        Returns True when a bullet was successfully spawned.
        """
        if self._shoot_cool > 0:
            return False
        dx = mx - self.x
        dy = my - self.y
        dist = math.hypot(dx, dy)
        if dist == 0:
            return False
        bullet = bullet_pool.get()
        if bullet is None:
            return False
        bullet.activate(self.x, self.y, dx / dist, dy / dist)
        self._shoot_cool = BULLET_COOLDOWN
        return True

    def take_damage(self, amount: int):
        self.health -= amount
        self._hit_flash = 0.15   # trigger red-flash animation
        if self.health <= 0:
            self.health = 0
            self.alive  = False

    # ── Drawing ───────────────────────────────────────────────────────────────

    def draw(self, surface: pygame.Surface):
        ix, iy = int(self.x), int(self.y)

        # Body circle – flashes red when the player takes damage
        body_color = RED if self._hit_flash > 0 else PLAYER_COLOR
        pygame.draw.circle(surface, body_color, (ix, iy), self.radius)
        pygame.draw.circle(surface, WHITE,      (ix, iy), self.radius, 2)

        # Gun barrel – a short line extending from center in the aim direction,
        # providing clear visual feedback of where shots will travel
        rad = math.radians(self._angle)
        tip = (ix + math.cos(rad) * (self.radius + 9),
               iy - math.sin(rad) * (self.radius + 9))
        pygame.draw.line(surface, WHITE, (ix, iy), (int(tip[0]), int(tip[1])), 4)
