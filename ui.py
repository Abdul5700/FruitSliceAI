"""Reusable modern UI drawing primitives and hand-dwell buttons."""
from __future__ import annotations
import pygame
from settings import ACCENT_COLOR, TEXT_COLOR, MUTED_TEXT


class Button:
    def __init__(self, label: str, center: tuple[int, int], size=(300, 58)) -> None:
        self.label, self.rect, self.dwell = label, pygame.Rect(0, 0, *size), 0.0
        self.rect.center = center
    def update(self, point: tuple[float, float] | None, dt: float) -> bool:
        active = point is not None and self.rect.collidepoint(point)
        self.dwell = min(.85, self.dwell + dt) if active else max(0, self.dwell - dt * 3)
        if self.dwell >= .85: self.dwell = 0; return True
        return False
    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        selected = self.dwell > 0
        # Shadow, subtle highlight, and a clear dwell meter make hand selection
        # readable even when the player is moving quickly.
        shadow = self.rect.move(0, 5)
        pygame.draw.rect(surface, (8, 12, 32), shadow, border_radius=18)
        fill = (49, 61, 112) if selected else (34, 45, 83)
        pygame.draw.rect(surface, fill, self.rect, border_radius=18)
        pygame.draw.line(surface, (91, 112, 171), (self.rect.x + 18, self.rect.y + 2), (self.rect.right - 18, self.rect.y + 2), 2)
        pygame.draw.rect(surface, ACCENT_COLOR if selected else (117, 145, 211), self.rect, 2, border_radius=18)
        if selected:
            progress_width = int((self.rect.width - 12) * self.dwell / .85)
            pygame.draw.rect(surface, ACCENT_COLOR, (self.rect.x + 6, self.rect.bottom - 8, progress_width, 4), border_radius=3)
        image = font.render(self.label, True, TEXT_COLOR)
        surface.blit(image, image.get_rect(center=(self.rect.centerx, self.rect.centery - (2 if selected else 0))))


def text(surface, font, value, pos, color=TEXT_COLOR, center=True):
    image = font.render(value, True, color); surface.blit(image, image.get_rect(center=pos) if center else pos)


HAND_CONNECTIONS = (
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (0, 9), (9, 10), (10, 11), (11, 12),
    (0, 13), (13, 14), (14, 15), (15, 16),
    (0, 17), (17, 18), (18, 19), (19, 20), (5, 9), (9, 13), (13, 17),
)


def camera_preview(surface: pygame.Surface, frame, landmarks=(), pos=(16, 16), size=(240, 180)) -> None:
    if frame is None: return
    image = pygame.image.frombuffer(frame.tobytes(), (frame.shape[1], frame.shape[0]), "RGB")
    image = pygame.transform.smoothscale(image, size); surface.blit(image, pos)
    if landmarks:
        points = [(int(pos[0] + x * size[0]), int(pos[1] + y * size[1])) for x, y in landmarks]
        for start, end in HAND_CONNECTIONS:
            if start < len(points) and end < len(points):
                pygame.draw.line(surface, (51, 255, 183), points[start], points[end], 2)
        for index, point in enumerate(points):
            color = ACCENT_COLOR if index == 8 else (255, 244, 103)
            radius = 7 if index == 8 else 4
            pygame.draw.circle(surface, (20, 35, 55), point, radius + 2)
            pygame.draw.circle(surface, color, point, radius)
    pygame.draw.rect(surface, MUTED_TEXT, (*pos, *size), 2, border_radius=8)
    text(surface, pygame.font.Font(None, 20), "LIVE HAND TRACKING", (pos[0] + size[0] // 2, pos[1] + 13), TEXT_COLOR)
