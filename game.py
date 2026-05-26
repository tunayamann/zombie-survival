"""
game.py – Core game loop, state machine, and system orchestrator.

Architecture
------------
Game owns every subsystem (player, bullets, enemies, waves, UI, sound) and
coordinates them through a finite-state machine with the following states:

    MENU → NAME_INPUT → PLAYING ↔ PAUSED
    PLAYING → GAME_OVER  (player health reaches 0)
    PLAYING → WIN        (all 8 waves cleared)
    GAME_OVER / WIN → NAME_INPUT  (restart)

Collision pipeline (two-phase)
-------------------------------
1. Broad phase – SpatialGrid buckets enemies into 64-px cells; only bullets
   sharing a cell (or adjacent cell) are tested further.
2. Narrow phase – exact circle-circle distance check for each candidate pair.

This reduces average-case work from O(bullets × enemies) to near O(bullets).
"""

import math
import sys

import pygame

from bullet import BulletPool
from collision import SpatialGrid
from enemy import Enemy
from particles import spawn_death_burst
from player import Player
from settings import (DARK_GRAY, FPS, GRAY, GRID_COLS, GRID_ROWS,
                      LIGHT_GRAY, SCREEN_HEIGHT, SCREEN_WIDTH,
                      STATE_GAME_OVER, STATE_MENU, STATE_NAME_INPUT,
                      STATE_PAUSED, STATE_PLAYING, STATE_WIN, TILE_SIZE,
                      TOTAL_WAVES, UI_HEIGHT)
from sound_manager import SoundManager
from tile_map import create_random_map, grid_to_world, world_to_grid
from ui import UI
from wave_manager import EnemyPool, WaveManager


class Game:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.clock  = pygame.time.Clock()

        fl = pygame.font.SysFont("Arial", 52, bold=True)
        fm = pygame.font.SysFont("Arial", 28)
        fs = pygame.font.SysFont("Arial", 20)

        self.ui    = UI(screen, fl, fm, fs)
        self.sound = SoundManager()

        self.state   = STATE_MENU
        self._spatial = SpatialGrid(cell_size=64)

        # Name-input state
        self.player_name     = ""
        self._cursor_blink   = 0.0
        self._cursor_visible = True

        self._particles = []   # active Particle objects from death bursts

        # Populated by _start()
        self.grid       = None
        self.player     = None
        self.bullets    = None
        self.enemies    = None
        self.waves      = None
        self.score      = 0
        self._banner_t  = 0.0
        self._prev_wave = 0

    # ── Public entry point ────────────────────────────────────────────────────

    def run(self):
        while True:
            dt = min(self.clock.tick(FPS) / 1000.0, 0.05)
            self._handle_events()
            self._update(dt)
            self._draw()

    # ── Event handling ────────────────────────────────────────────────────────

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if self.state == STATE_MENU:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    self.state = STATE_NAME_INPUT

            elif self.state == STATE_NAME_INPUT:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if not self.player_name:
                            self.player_name = "Player"
                        self._start()
                    elif event.key == pygame.K_BACKSPACE:
                        self.player_name = self.player_name[:-1]
                    elif len(self.player_name) < 16 and event.unicode.isprintable():
                        self.player_name += event.unicode

            elif self.state == STATE_PLAYING:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.state = STATE_PAUSED

            elif self.state == STATE_PAUSED:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.state = STATE_PLAYING

            elif self.state in (STATE_GAME_OVER, STATE_WIN):
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self._start()
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

    # ── Game reset / start ────────────────────────────────────────────────────

    def _start(self):
        """Initialise or re-initialise all gameplay systems for a fresh run."""
        self.grid    = create_random_map(wave=1)
        self.player  = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.bullets = BulletPool()
        self.enemies = EnemyPool()
        self.waves   = WaveManager(self.enemies)
        self.score      = 0
        self._banner_t  = 0.0
        self._prev_wave = 0
        self._particles.clear()

        self.state = STATE_PLAYING
        self.waves.start()
        self._banner_t  = 2.0
        self._prev_wave = self.waves.current_wave
        self.sound.play("wave_start")

    # ── Update ────────────────────────────────────────────────────────────────

    def _update(self, dt: float):
        # Name-input only needs cursor blink logic
        if self.state == STATE_NAME_INPUT:
            self._cursor_blink += dt
            if self._cursor_blink >= 0.5:
                self._cursor_blink   = 0.0
                self._cursor_visible = not self._cursor_visible
            return

        if self.state != STATE_PLAYING:
            return

        keys = pygame.key.get_pressed()
        mx, my = pygame.mouse.get_pos()

        self.player.update_aim(mx, my)
        self.player.update(keys, dt, self.grid)

        # Auto-fire while left mouse button is held
        if pygame.mouse.get_pressed()[0]:
            if self.player.try_shoot(self.bullets, mx, my):
                self.sound.play("shoot")

        self.bullets.update(dt, self.grid)

        # Detect player damage by comparing health before and after enemy update
        hp_before = self.player.health
        self.enemies.update(dt, self.grid, self.player)
        if self.player.health < hp_before:
            self.sound.play("player_hit")

        self._resolve_bullet_enemy_collisions()

        # Update particles and discard expired ones
        for p in self._particles:
            p.update(dt)
        self._particles = [p for p in self._particles if p.alive]

        if self._banner_t > 0:
            self._banner_t -= dt

        self.waves.update(dt, self.grid)

        # On wave transition: regenerate the map and reset player to center
        if self.waves.current_wave != self._prev_wave:
            if self.waves.current_wave <= TOTAL_WAVES:
                self.grid = create_random_map(self.waves.current_wave)
                self.player.x = SCREEN_WIDTH  // 2
                self.player.y = SCREEN_HEIGHT // 2
                self._banner_t = 2.0
                self.sound.play("wave_start")
            self._prev_wave = self.waves.current_wave

        # State transitions
        if not self.player.alive:
            self.state = STATE_GAME_OVER
            self.sound.play("game_over")
        elif self.waves.game_won and self.enemies.all_dead():
            self.state = STATE_WIN
            self.sound.play("win")

    # ── Collision resolution ──────────────────────────────────────────────────

    def _resolve_bullet_enemy_collisions(self):
        """
        Two-phase collision detection:
          Broad phase  – spatial hash grid reduces candidate pairs.
          Narrow phase – circle-circle distance test for each candidate.
        A bullet is deactivated on the first enemy it hits; one bullet = one hit.
        """
        self._spatial.clear()
        for e in self.enemies.active_enemies():
            self._spatial.add(e, e.x, e.y)

        for b in self.bullets.active_bullets():
            for e in self._spatial.get_nearby(b.x, b.y):
                if not e.active:
                    continue
                if math.hypot(b.x - e.x, b.y - e.y) <= b.radius + e.radius:
                    killed = e.take_damage(b.damage)
                    b.deactivate()
                    if killed:
                        self.score += 10 * self.waves.current_wave
                        self.sound.play("zombie_die")
                        self._particles += spawn_death_burst(e.x, e.y)
                    break

    # ── Drawing ───────────────────────────────────────────────────────────────

    def _draw(self):
        if self.state == STATE_MENU:
            self.ui.draw_menu()

        elif self.state == STATE_NAME_INPUT:
            self.ui.draw_name_input(self.player_name, self._cursor_visible)

        elif self.state in (STATE_PLAYING, STATE_PAUSED):
            self._draw_world()
            self.ui.draw_hud(self.player, self.waves.current_wave,
                             TOTAL_WAVES, self.score, self.player_name)
            self.ui.draw_wave_banner(self.waves.current_wave, self._banner_t)
            if self.state == STATE_PAUSED:
                self.ui.draw_pause()

        elif self.state == STATE_GAME_OVER:
            self.ui.draw_game_over(self.score, self.waves.current_wave)

        elif self.state == STATE_WIN:
            self.ui.draw_win(self.score)

        pygame.display.flip()

    def _draw_world(self):
        """Render the tile grid, then bullets, enemies, and player (depth order)."""
        self.screen.fill(DARK_GRAY)

        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                x = c * TILE_SIZE
                y = r * TILE_SIZE + UI_HEIGHT
                if self.grid[r][c] == 1:
                    pygame.draw.rect(self.screen, GRAY,
                                     (x, y, TILE_SIZE, TILE_SIZE))
                    pygame.draw.rect(self.screen, LIGHT_GRAY,
                                     (x, y, TILE_SIZE, TILE_SIZE), 1)
                else:
                    pygame.draw.rect(self.screen, (42, 42, 42),
                                     (x, y, TILE_SIZE, TILE_SIZE))
                    pygame.draw.rect(self.screen, (52, 52, 52),
                                     (x, y, TILE_SIZE, TILE_SIZE), 1)

        self.bullets.draw(self.screen)
        for p in self._particles:
            p.draw(self.screen)
        self.enemies.draw(self.screen)
        self.player.draw(self.screen)
