"""
ui.py – All screen-rendering that is not part of the game world.

Responsibilities:
  • In-game HUD: health bar, wave counter, score, player name.
  • Overlay screens: main menu, name-input, pause, game-over, win.
  • Wave announcement banner with alpha fade.

All drawing is done through the pygame.Surface passed at construction; the UI
class itself is stateless between frames (callers provide current values).
"""

import pygame

from settings import (DARK_GRAY, GREEN, HEALTH_BAR_HEIGHT, HEALTH_BAR_WIDTH,
                      LIGHT_GRAY, RED, SCREEN_HEIGHT, SCREEN_WIDTH, UI_HEIGHT,
                      WHITE, YELLOW, GRAY)


class UI:
    def __init__(self, screen: pygame.Surface,
                 font_large: pygame.font.Font,
                 font_med:   pygame.font.Font,
                 font_small: pygame.font.Font):
        self.screen = screen
        self.fl     = font_large
        self.fm     = font_med
        self.fs     = font_small

    # ── In-game HUD ───────────────────────────────────────────────────────────

    def draw_hud(self, player, wave: int, total_waves: int, score: int,
                 player_name: str = ""):
        pygame.draw.rect(self.screen, DARK_GRAY, (0, 0, SCREEN_WIDTH, UI_HEIGHT))
        pygame.draw.line(self.screen, GRAY,
                         (0, UI_HEIGHT), (SCREEN_WIDTH, UI_HEIGHT), 2)

        # Health bar – color shifts green → yellow → red as HP falls
        label = self.fs.render("HP", True, WHITE)
        self.screen.blit(label, (10, 11))

        bx, by = 36, 11
        ratio = max(0.0, player.health / player.max_health)
        bar_color = GREEN if ratio > 0.5 else YELLOW if ratio > 0.25 else RED
        pygame.draw.rect(self.screen, RED,       (bx, by, HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT))
        pygame.draw.rect(self.screen, bar_color, (bx, by, int(HEALTH_BAR_WIDTH * ratio), HEALTH_BAR_HEIGHT))
        pygame.draw.rect(self.screen, WHITE,     (bx, by, HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT), 1)

        # Player name displayed immediately right of the health bar
        if player_name:
            name_txt = self.fs.render(player_name, True, LIGHT_GRAY)
            self.screen.blit(name_txt, (245, 12))

        # Wave counter centered horizontally
        wave_txt = self.fm.render(f"Wave  {wave} / {total_waves}", True, YELLOW)
        self.screen.blit(wave_txt,
                         (SCREEN_WIDTH // 2 - wave_txt.get_width() // 2, 7))

        # Score right-aligned
        score_txt = self.fm.render(f"Score: {score}", True, WHITE)
        self.screen.blit(score_txt,
                         (SCREEN_WIDTH - score_txt.get_width() - 10, 7))

    # ── Overlay screens ───────────────────────────────────────────────────────

    def draw_name_input(self, name: str, cursor_visible: bool):
        """
        Render the name-entry screen.
        The blinking cursor is implemented by the caller toggling cursor_visible
        every 0.5 s; this method simply appends '|' or ' ' accordingly.
        """
        self.screen.fill(DARK_GRAY)
        self._centre(self.fl.render("ZOMBIE  SURVIVAL", True, RED), 150)
        self._centre(self.fm.render("Enter your name:", True, YELLOW), 260)

        display = name + ("|" if cursor_visible else " ")
        box_surf = self.fm.render(display, True, WHITE)
        bx = SCREEN_WIDTH // 2 - 150
        by = 300
        pygame.draw.rect(self.screen, (60, 60, 60), (bx, by, 300, 40))
        pygame.draw.rect(self.screen, LIGHT_GRAY,   (bx, by, 300, 40), 2)
        self.screen.blit(box_surf, (bx + 10, by + 8))

        self._centre(self.fs.render("Press ENTER to start", True, LIGHT_GRAY), 380)

    def draw_menu(self):
        self.screen.fill(DARK_GRAY)
        self._centre(self.fl.render("ZOMBIE  SURVIVAL", True, RED),           150)
        self._centre(self.fm.render("Survive all 8 waves to win!", True, YELLOW), 225)

        controls = ["WASD — Move",
                    "Mouse — Aim",
                    "Hold Left Click — Shoot",
                    "ESC — Pause"]
        for i, line in enumerate(controls):
            self._centre(self.fs.render(line, True, LIGHT_GRAY), 295 + i * 30)

        self._centre(self.fm.render("Press  ENTER  to Play", True, GREEN), 450)

    def draw_pause(self):
        # Semi-transparent overlay drawn on top of the game world
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        self._centre(self.fl.render("PAUSED", True, YELLOW),
                     SCREEN_HEIGHT // 2 - 40)
        self._centre(self.fs.render("Press ESC to Resume", True, WHITE),
                     SCREEN_HEIGHT // 2 + 20)

    def draw_game_over(self, score: int, wave: int):
        self.screen.fill(DARK_GRAY)
        self._centre(self.fl.render("GAME  OVER", True, RED),                 170)
        self._centre(self.fm.render(f"Reached Wave: {wave}", True, YELLOW),   275)
        self._centre(self.fm.render(f"Score: {score}",        True, WHITE),   320)
        self._centre(self.fs.render("ENTER — Restart    ESC — Quit",
                                    True, LIGHT_GRAY),                         420)

    def draw_win(self, score: int):
        self.screen.fill(DARK_GRAY)
        self._centre(self.fl.render("YOU  WIN!", True, GREEN),                 170)
        self._centre(self.fm.render("All 8 waves survived!", True, YELLOW),    260)
        self._centre(self.fm.render(f"Final Score: {score}", True, WHITE),     315)
        self._centre(self.fs.render("ENTER — Play Again    ESC — Quit",
                                    True, LIGHT_GRAY),                          420)

    def draw_wave_banner(self, wave: int, timer: float):
        """
        Render a fading 'WAVE N' announcement for the first 2 s of each wave.
        Alpha is derived from the remaining timer so the text fades out smoothly.
        """
        if timer <= 0:
            return
        alpha = min(255, int(timer * 200))
        surf  = self.fl.render(f"WAVE  {wave}", True, YELLOW)
        surf.set_alpha(alpha)
        self.screen.blit(surf, (SCREEN_WIDTH  // 2 - surf.get_width()  // 2,
                                 SCREEN_HEIGHT // 2 - surf.get_height() // 2))

    # ── Helper ────────────────────────────────────────────────────────────────

    def _centre(self, surf: pygame.Surface, y: int):
        """Blit a surface horizontally centered at vertical position y."""
        self.screen.blit(surf, (SCREEN_WIDTH // 2 - surf.get_width() // 2, y))
