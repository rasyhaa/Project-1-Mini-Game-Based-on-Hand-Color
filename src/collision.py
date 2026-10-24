import math
import random
from typing import List, Tuple
import pygame
import config
from src.player import PlayerCar
from src.traffic import TrafficManager, NPC
from src.asset_manager import AssetManager

class Particle:
    """Individual visual spark or smoke particle for crash feedback."""

    def __init__(self, x: float, y: float, color: Tuple[int, int, int]):
        self.x = x
        self.y = y
        self.color = color

        angle = random.uniform(0, 2.0 * math.pi)
        speed = random.uniform(80.0, 320.0)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed

        self.lifetime = random.uniform(0.3, 0.6)
        self.age = 0.0
        self.size = random.uniform(3.0, 7.0)

    @property
    def is_alive(self) -> bool:
        return self.age < self.lifetime

    def update(self, dt: float):
        self.age += dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        # Drag & gravity
        self.vx *= 0.94
        self.vy *= 0.94

    def draw(self, surface: pygame.Surface):
        if not self.is_alive:
            return
        progress = self.age / self.lifetime
        current_size = max(1.0, self.size * (1.0 - progress))
        # Fade color
        alpha_factor = 1.0 - progress
        r = int(self.color[0] * alpha_factor)
        g = int(self.color[1] * alpha_factor)
        b = int(self.color[2] * alpha_factor)
        pygame.draw.circle(surface, (r, g, b), (int(self.x), int(self.y)), int(current_size))


class CollisionManager:
    """Handles collision checks, invulnerability logic, and crash particle effects."""

    def __init__(self, asset_manager: AssetManager):
        self.asset_manager = asset_manager
        self.particles: List[Particle] = []

    def reset(self):
        """Clears all active particles."""
        self.particles.clear()

    def spawn_crash_particles(self, x: float, y: float):
        """Creates an energetic burst of flame and spark particles at impact point."""
        colors = [
            (255, 230, 40),  # Yellow spark
            (255, 90, 20),   # Orange flame
            (240, 30, 30),   # Red fire
            (220, 240, 255)  # White-hot flash
        ]
        for _ in range(45):
            c = random.choice(colors)
            self.particles.append(Particle(x, y, c))

    def check_collisions(self, player: PlayerCar, traffic_manager: TrafficManager) -> bool:
        """
        Evaluates collision between player hitbox and active NPC hitboxes.
        Returns True if a life was lost this frame, False otherwise.
        """
        if player.is_invulnerable or player.lives <= 0:
            return False

        player_box = player.hitbox

        for npc in traffic_manager.npcs:
            if not npc.active:
                continue

            if player_box.colliderect(npc.hitbox):
                # Calculate collision midpoint for particle burst
                cx = (player.x + npc.x) / 2.0
                cy = (player.y + npc.y) / 2.0

                # Deduct exactly 1 life and initiate invulnerability grace period
                damaged = player.hit()

                if damaged:
                    self.spawn_crash_particles(cx, cy)
                    self.asset_manager.play_sound("audio/collision.wav", volume=0.85)

                    # Remove or deactivate the colliding NPC so it cannot multi-collide
                    npc.active = False
                    return True

        return False

    def update(self, dt: float):
        """Updates particle physics."""
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.is_alive]

    def draw(self, surface: pygame.Surface):
        """Renders collision visual particles."""
        for p in self.particles:
            p.draw(surface)
