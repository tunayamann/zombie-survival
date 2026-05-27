"""
wave_manager.py – Enemy object pool and wave progression controller.

EnemyPool
---------
Maintains a fixed array of Enemy instances that live for the entire session.
Requesting an enemy retrieves an inactive slot and reconfigures it rather than
allocating a new object, avoiding garbage-collection pauses.

WaveManager
-----------
Drives the game's wave progression through three internal phases:
  • Drip-spawn: enemies are released one by one every SPAWN_DELAY seconds
    rather than all at once, so the player faces a manageable trickle that
    builds tension without an overwhelming instant rush.
  • Wait-for-clear: once all enemies are spawned, the wave is held open until
    every enemy is dead, ensuring the player earns each transition.
  • Rest: a brief between-wave pause gives the player a moment to breathe and
    reposition before the next wave's map is generated.
"""

import random

from enemy import Enemy
from settings import (BETWEEN_WAVE_DELAY, ENEMY_POOL_SIZE, SPAWN_DELAY,
                      TOTAL_WAVES, WAVE_BASE_COUNT, WAVE_COUNT_INCREMENT,
                      WAVE_MAX_COUNT)
from tile_map import grid_to_world


# ── Object pool ───────────────────────────────────────────────────────────────

class EnemyPool:
    def __init__(self, size: int = ENEMY_POOL_SIZE):
        self._pool = [Enemy() for _ in range(size)]

    def get(self) -> Enemy | None:
        """Return the first inactive enemy from the pool, or None if exhausted."""
        for e in self._pool:
            if not e.active:
                return e
        return None

    def active_enemies(self):
        return [e for e in self._pool if e.active]

    def all_dead(self) -> bool:
        return all(not e.active for e in self._pool)

    def update(self, dt, grid, player):
        # Build the active list once per frame; each enemy receives it so the
        # separation-steering calculation does not re-scan the pool repeatedly
        active = [e for e in self._pool if e.active]
        for e in active:
            e.update(dt, grid, player, neighbours=active)

    def draw(self, surface):
        for e in self._pool:
            if e.active:
                e.draw(surface)


# ── Wave controller ───────────────────────────────────────────────────────────

class WaveManager:
    def __init__(self, pool: EnemyPool):
        self._pool          = pool
        self.current_wave   = 0
        self.total_waves    = TOTAL_WAVES
        self.game_won       = False

        self._wave_active   = False
        self._spawn_queue   = 0      # enemies still waiting to be spawned
        self._spawn_timer   = 0.0
        self._between_timer = 0.0

    def start(self):
        self.current_wave = 0
        self.game_won     = False
        self._next_wave()

    # ── Internal ──────────────────────────────────────────────────────────────

    def _next_wave(self):
        self.current_wave += 1
        if self.current_wave > self.total_waves:
            self.game_won     = True
            self._wave_active = False
            return
        # Enemy count grows linearly up to WAVE_MAX_COUNT, then stays flat
        count = min(WAVE_BASE_COUNT + (self.current_wave - 1) * WAVE_COUNT_INCREMENT,
                    WAVE_MAX_COUNT)
        self._spawn_queue = count
        self._spawn_timer = 0.0
        self._wave_active = True

    def _spawn_position(self, grid):
        """
        Choose a random walkable tile on the second row or column from each edge.
        This band is always kept free by create_random_map, so candidates
        are guaranteed to exist in every generated layout.
        """
        rows, cols = len(grid), len(grid[0])
        candidates = []
        for c in range(1, cols - 1):
            if grid[1][c]        == 0: candidates.append((1,        c))
            if grid[rows - 2][c] == 0: candidates.append((rows - 2, c))
        for r in range(1, rows - 1):
            if grid[r][1]        == 0: candidates.append((r,        1))
            if grid[r][cols - 2] == 0: candidates.append((r, cols - 2))
        if not candidates:
            return 64, 64   # fallback: should never be reached
        r, c = random.choice(candidates)
        return grid_to_world(r, c)

    # ── Public update ─────────────────────────────────────────────────────────

    def update(self, dt: float, grid):
        if self.game_won:
            return

        if self._wave_active:
            if self._spawn_queue > 0:
                # Drip-spawn: release one enemy per SPAWN_DELAY interval
                self._spawn_timer += dt
                if self._spawn_timer >= SPAWN_DELAY:
                    self._spawn_timer -= SPAWN_DELAY
                    self._spawn_queue -= 1
                    x, y = self._spawn_position(grid)
                    e = self._pool.get()
                    if e:
                        e.activate(x, y, self.current_wave)
            else:
                # All enemies spawned; wait until every one is dead
                if self._pool.all_dead():
                    self._wave_active   = False
                    self._between_timer = 0.0
        else:
            if not self.game_won:
                self._between_timer += dt
                if self._between_timer >= BETWEEN_WAVE_DELAY:
                    self._next_wave()
