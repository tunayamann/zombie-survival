"""
main.py – Application entry point.

Initialises pygame, creates the display surface, and hands control to the
Game object which owns the main loop and all subsystems.
"""

import sys

try:
    import pygame
except ImportError:
    print("pygame not found. Run:  pip install pygame")
    sys.exit(1)

from settings import FPS, SCREEN_HEIGHT, SCREEN_WIDTH, TITLE
from game import Game


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(TITLE)
    pygame.mouse.set_visible(True)

    Game(screen).run()


if __name__ == "__main__":
    main()
