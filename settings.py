"""
settings.py – Global constants for Zombie Survival.

Centralising every magic number here makes tuning and balancing straightforward:
changing a value in one place propagates throughout the entire codebase.
"""

# ── Display ───────────────────────────────────────────────────────────────────
SCREEN_WIDTH  = 800
SCREEN_HEIGHT = 600
FPS           = 60
TITLE         = "Zombie Survival"

# ── Grid / Tile ───────────────────────────────────────────────────────────────
# The playable area sits below the HUD bar.  Dividing by TILE_SIZE gives the
# exact number of grid cells that fill the screen with no partial tiles.
TILE_SIZE  = 32
GRID_COLS  = SCREEN_WIDTH  // TILE_SIZE          # 25 columns
GRID_ROWS  = (SCREEN_HEIGHT - 40) // TILE_SIZE   # 17 rows  (game area below UI bar)
UI_HEIGHT  = 40                                   # pixel height of the HUD strip

# ── Colors ────────────────────────────────────────────────────────────────────
BLACK      = (  0,   0,   0)
WHITE      = (255, 255, 255)
RED        = (220,  50,  50)
GREEN      = ( 50, 200,  50)
YELLOW     = (255, 210,   0)
GRAY       = (100, 100, 100)
DARK_GRAY  = ( 30,  30,  30)
LIGHT_GRAY = (160, 160, 160)
ORANGE     = (255, 140,   0)

# ── Player ────────────────────────────────────────────────────────────────────
PLAYER_SPEED   = 200          # pixels per second
PLAYER_HEALTH  = 100
PLAYER_RADIUS  = 14           # used for rendering and collision probes
PLAYER_COLOR   = ( 50, 200,  50)

# ── Bullet ───────────────────────────────────────────────────────────────────
BULLET_SPEED     = 450        # pixels per second
BULLET_DAMAGE    = 25
BULLET_RADIUS    = 5
BULLET_COLOR     = (255, 210,   0)
BULLET_POOL_SIZE = 60         # pre-allocated pool size; prevents mid-game allocation
BULLET_COOLDOWN  = 0.18       # minimum seconds between consecutive shots

# ── Enemy ─────────────────────────────────────────────────────────────────────
ENEMY_SPEED          = 75     # base pixels per second; scales +5 per wave
ENEMY_HEALTH_BASE    = 50     # base HP; scales +20 per wave
ENEMY_DAMAGE         = 10     # damage dealt per melee hit
ENEMY_RADIUS         = 14
ENEMY_COLOR          = (200,  50,  50)
# A* is expensive; recalculating every frame would tank performance.
# 0.45 s gives responsive tracking while keeping CPU usage acceptable.
ENEMY_PATH_UPDATE    = 0.45   # seconds between A* recalculations per enemy
ENEMY_ATTACK_RANGE   = 18     # pixels beyond ENEMY_RADIUS that triggers melee
ENEMY_ATTACK_COOL    = 1.0    # seconds between consecutive melee hits
ENEMY_POOL_SIZE      = 60     # pre-allocated pool; mirrors BULLET_POOL_SIZE pattern

# ── Waves ─────────────────────────────────────────────────────────────────────
WAVE_BASE_COUNT      = 5      # enemies in wave 1
WAVE_COUNT_INCREMENT = 3      # additional enemies per subsequent wave
WAVE_MAX_COUNT       = 17     # enemy count is capped here from wave 5 onward
TOTAL_WAVES          = 8
SPAWN_DELAY          = 0.5    # seconds between individual enemy spawns (drip-spawn)
BETWEEN_WAVE_DELAY   = 3.0    # rest period between waves

# ── UI ────────────────────────────────────────────────────────────────────────
HEALTH_BAR_WIDTH  = 200
HEALTH_BAR_HEIGHT = 20

# ── Game states ───────────────────────────────────────────────────────────────
# The game is driven by an explicit finite-state machine.  Each string token
# represents one mutually exclusive mode of operation.
STATE_MENU       = "menu"
STATE_NAME_INPUT = "name_input"
STATE_PLAYING    = "playing"
STATE_PAUSED     = "paused"
STATE_GAME_OVER  = "game_over"
STATE_WIN        = "win"
