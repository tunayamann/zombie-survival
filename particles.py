"""
particles.py – Lightweight particle system for death burst visual effects.

Each Particle is a plain data object: position, velocity, color, radius, and
lifetime.  Color and radius fade proportionally to remaining lifetime so
particles naturally dissipate as they fly outward.

spawn_death_burst() is the public factory function; it returns a ready-made
list of particles centred at the enemy's death position.  Game collects these
lists into a single list that is updated and pruned each frame.
"""

import math
import random

import pygame


class Particle:
    def __init__(self, x: float, y: float, vx: float, vy: float,
                 color: tuple, radius: int = 5, lifetime: float = 0.45):
        self.x        = x
        self.y        = y
        self.vx       = vx
        self.vy       = vy
        self.color    = color
        self.radius   = radius
        self.lifetime = lifetime
        self.age      = 0.0

    @property
    def alive(self) -> bool:
        return self.age < self.lifetime

    def update(self, dt: float):
        self.age += dt
        self.x   += self.vx * dt
        self.y   += self.vy * dt

    def draw(self, surface: pygame.Surface):
        # Linearly interpolate size and brightness toward zero
        ratio = max(0.0, 1.0 - self.age / self.lifetime)
        r     = max(1, int(self.radius * ratio))
        color = tuple(int(c * ratio) for c in self.color)
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), r)


def spawn_death_burst(x: float, y: float, count: int = 7) -> list:
    """
    Create count particles flying outward from (x, y) at random angles.
    Colors are sampled from a warm palette (orange, red, yellow) to sell
    the 'enemy exploding' feel without needing external assets.
    """
    palette = [
        (255,  80,   0),   # orange
        (220,  50,  50),   # red
        (255, 200,   0),   # yellow
    ]
    particles = []
    for _ in range(count):
        angle    = random.uniform(0, 2 * math.pi)
        speed    = random.uniform(60, 160)
        color    = random.choice(palette)
        radius   = random.randint(3, 6)
        lifetime = random.uniform(0.30, 0.50)
        particles.append(Particle(
            x, y,
            math.cos(angle) * speed,
            math.sin(angle) * speed,
            color, radius, lifetime
        ))
    return particles
