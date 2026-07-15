"""Flying fruit entity and procedural fruit art."""
from __future__ import annotations

import math
import random
import pygame

FRUITS = [((247, 75, 86), (255, 179, 171), "apple"), ((255, 191, 52), (255, 231, 120), "orange"),
          ((117, 207, 88), (197, 247, 149), "lime"), ((218, 82, 190), (250, 150, 220), "berry")]


class Fruit:
    def __init__(self, width: int, height: int, speed: float) -> None:
        self.x, self.y = random.uniform(80, width - 80), height + 55
        self.radius = random.randint(31, 43)
        self.vx, self.vy = random.uniform(-180, 180) * speed, random.uniform(-850, -690) * speed
        self.color, self.light, self.kind = random.choice(FRUITS)
        self.rotation, self.spin = random.random() * 360, random.uniform(-220, 220)
        self.sliced = False

    def update(self, dt: float) -> None:
        self.x += self.vx * dt; self.y += self.vy * dt
        self.vy += 760 * dt; self.rotation += self.spin * dt

    def draw(self, surface: pygame.Surface) -> None:
        pos = (int(self.x), int(self.y))
        pygame.draw.circle(surface, (0, 0, 0), (pos[0] + 5, pos[1] + 8), self.radius)
        pygame.draw.circle(surface, self.color, pos, self.radius)
        pygame.draw.circle(surface, self.light, (pos[0] - self.radius // 3, pos[1] - self.radius // 3), self.radius // 4)
        pygame.draw.line(surface, (74, 58, 28), (pos[0], pos[1] - self.radius + 5), (pos[0] + 4, pos[1] - self.radius - 10), 5)
        pygame.draw.ellipse(surface, (82, 182, 83), (pos[0] + 2, pos[1] - self.radius - 12, 17, 9))

    def is_offscreen(self, height: int) -> bool:
        return self.y - self.radius > height + 15

    def hit(self, a: tuple[float, float], b: tuple[float, float]) -> bool:
        ax, ay = a; bx, by = b; dx, dy = bx - ax, by - ay
        length_sq = dx * dx + dy * dy
        t = 0 if length_sq == 0 else max(0, min(1, ((self.x - ax) * dx + (self.y - ay) * dy) / length_sq))
        return math.dist((self.x, self.y), (ax + t * dx, ay + t * dy)) < self.radius + 10
