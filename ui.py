import pygame

from settings import (DARK_GRAY, GREEN, HEALTH_BAR_HEIGHT, HEALTH_BAR_WIDTH,
                      LIGHT_GRAY, RED, SCREEN_HEIGHT, SCREEN_WIDTH, UI_HEIGHT,
                      WHITE, YELLOW, GRAY)


class UI:
    def __init__(self, screen: pygame.Surface,
                 font_large: pygame.font.Font,
                 font_med:   pygame.font.Font,
                 font_small: pygame.font.Font):
        self.screen     = screen
        self.fl         = font_large
        self.fm         = font_med
        self.fs         = font_small

    # ── In-game HUD ───────────────────────────────────────────────────────────

    def draw_hud(self, player, wave: int, total_waves: int, score: int):
        pygame.draw.rect(self.screen, DARK_GRAY, (0, 0, SCREEN_WIDTH, UI_HEIGHT))
        pygame.draw.line(self.screen, GRAY,
                         (0, UI_HEIGHT), (SCREEN_WIDTH, UI_HEIGHT), 2)

        # Health bar
        label = self.fs.render("HP", True, WHITE)
        self.screen.blit(label, (10, 11))

        bx, by = 36, 11
        ratio  = max(0.0, player.health / player.max_health)
        bar_color = GREEN if ratio > 0.5 else YELLOW if ratio > 0.25 else RED
        pygame.draw.rect(self.screen, RED,       (bx, by, HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT))
        pygame.draw.rect(self.screen, bar_color, (bx, by, int(HEALTH_BAR_WIDTH * ratio), HEALTH_BAR_HEIGHT))
        pygame.draw.rect(self.screen, WHITE,     (bx, by, HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT), 1)
        hp_txt = self.fs.render(f"{player.health}/{player.max_health}", True, WHITE)
        self.screen.blit(hp_txt, (bx + 5, by + 2))

        # Wave counter (centered)
        wave_txt = self.fm.render(f"Wave  {wave} / {total_waves}", True, YELLOW)
        self.screen.blit(wave_txt,
                         (SCREEN_WIDTH // 2 - wave_txt.get_width() // 2, 7))

        # Score (right-aligned)
        score_txt = self.fm.render(f"Score: {score}", True, WHITE)
        self.screen.blit(score_txt,
                         (SCREEN_WIDTH - score_txt.get_width() - 10, 7))

    # ── Overlay screens ───────────────────────────────────────────────────────

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
        """Fading 'WAVE N' announcement shown for the first 2 s of each wave."""
        if timer <= 0:
            return
        alpha = min(255, int(timer * 200))
        surf  = self.fl.render(f"WAVE  {wave}", True, YELLOW)
        surf.set_alpha(alpha)
        self.screen.blit(surf, (SCREEN_WIDTH  // 2 - surf.get_width()  // 2,
                                 SCREEN_HEIGHT // 2 - surf.get_height() // 2))

    # ── Helper ────────────────────────────────────────────────────────────────

    def _centre(self, surf: pygame.Surface, y: int):
        self.screen.blit(surf, (SCREEN_WIDTH // 2 - surf.get_width() // 2, y))
