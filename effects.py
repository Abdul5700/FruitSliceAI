"""Lightweight particles, floating labels, and synthesized game sounds."""
from __future__ import annotations
import math
import random
import numpy as np
import pygame


class Particle:
    def __init__(self, x: float, y: float, color: tuple[int, int, int], explosion: bool = False) -> None:
        angle = random.random() * math.tau; speed = random.uniform(80, 400 if explosion else 250)
        self.x, self.y, self.vx, self.vy = x, y, math.cos(angle)*speed, math.sin(angle)*speed
        self.color, self.life, self.max_life, self.size = color, random.uniform(.35, .8), 0, random.randint(3, 9)
        self.max_life = self.life
    def update(self, dt: float) -> bool:
        self.x += self.vx*dt; self.y += self.vy*dt; self.vy += 450*dt; self.life -= dt
        return self.life > 0
    def draw(self, s: pygame.Surface) -> None:
        alpha = int(255 * self.life / self.max_life)
        layer = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
        pygame.draw.circle(layer, (*self.color, alpha), (self.size, self.size), self.size)
        s.blit(layer, (self.x-self.size, self.y-self.size))


class Effects:
    def __init__(self) -> None:
        self.particles: list[Particle] = []; self.labels: list[list] = []
    def burst(self, x: float, y: float, color: tuple[int, int, int], count: int = 18, explosion: bool = False) -> None:
        self.particles.extend(Particle(x, y, color, explosion) for _ in range(count))
    def label(self, text: str, x: float, y: float, color: tuple[int, int, int]) -> None:
        self.labels.append([text, x, y, color, 1.0])
    def update(self, dt: float) -> None:
        self.particles = [p for p in self.particles if p.update(dt)]
        for item in self.labels: item[2] -= 55*dt; item[4] -= dt
        self.labels = [x for x in self.labels if x[4] > 0]
    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        for p in self.particles: p.draw(surface)
        for text, x, y, color, life in self.labels:
            image = font.render(text, True, color); image.set_alpha(int(255*life))
            surface.blit(image, image.get_rect(center=(x, y)))


class SoundBank:
    """Procedurally creates tiny sounds; absence of external files never breaks play."""
    def __init__(self) -> None:
        self.enabled = False; self.sounds = {}; self.music = None
        try:
            if not pygame.mixer.get_init(): pygame.mixer.init(frequency=22050, size=-16, channels=1)
            self.enabled = True
            self.sounds = {"slice": self._tone(580, .09), "click": self._tone(740, .06), "boom": self._tone(75, .35), "gameover": self._tone(170, .45)}
            self.music = self._music()
            self.music.set_volume(.10)
            self.music.play(loops=-1)
        except pygame.error: pass
    def _tone(self, frequency: int, duration: float) -> pygame.mixer.Sound:
        samples = int(22050 * duration); t = np.arange(samples)/22050
        wave = (np.sin(2*np.pi*frequency*t) * np.exp(-7*t) * 0.28 * 32767).astype(np.int16)
        return pygame.mixer.Sound(buffer=wave.tobytes())
    def _music(self) -> pygame.mixer.Sound:
        """A gentle generated loop keeps the portfolio project self-contained."""
        sample_rate, duration = 22050, 4.0
        t = np.arange(int(sample_rate * duration)) / sample_rate
        wave = sum(np.sin(2*np.pi*f*t) for f in (110, 138, 165)) / 3
        # Soft repeating pulse rather than a continuous harsh tone.
        envelope = .35 + .25 * (np.sin(2*np.pi*.5*t) + 1) / 2
        raw = (wave * envelope * .20 * 32767).astype(np.int16)
        return pygame.mixer.Sound(buffer=raw.tobytes())
    def play(self, name: str) -> None:
        if self.enabled and name in self.sounds: self.sounds[name].play()
