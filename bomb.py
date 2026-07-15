"""Flying bomb hazard."""
from fruit import Fruit
import pygame


class Bomb(Fruit):
    def __init__(self, width: int, height: int, speed: float) -> None:
        super().__init__(width, height, speed)
        self.radius = 36

    def draw(self, surface: pygame.Surface) -> None:
        x, y, r = int(self.x), int(self.y), self.radius
        pygame.draw.circle(surface, (0, 0, 0), (x + 4, y + 6), r)
        pygame.draw.circle(surface, (46, 52, 70), (x, y), r)
        pygame.draw.circle(surface, (82, 91, 116), (x - 11, y - 12), 9)
        pygame.draw.line(surface, (229, 181, 71), (x + 8, y - r + 5), (x + 17, y - r - 13), 4)
        pygame.draw.circle(surface, (255, 109, 67), (x + 18, y - r - 15), 6)
