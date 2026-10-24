import math
import pygame
import config
from src.lane_manager import LaneManager

class PlayerCar:
    """Represents the player-controlled car."""

    def __init__(self, lane_manager: LaneManager, sprite: pygame.Surface):
        self.lane_manager = lane_manager
        self.sprite = sprite

        self.current_lane = config.PLAYER_START_LANE
        self.target_lane = config.PLAYER_START_LANE

        # Fixed vertical position (near bottom of the road)
        self.y = float(config.PLAYER_Y)

        # Horizontal position (locked to lane center)
        self.x = float(self.lane_manager.get_lane_center(self.current_lane))

        # Dimensions
        self.width = config.PLAYER_WIDTH
        self.height = config.PLAYER_HEIGHT

        # State & Health
        self.lives = config.PLAYER_LIVES
        self.invulnerable_timer = 0.0
        self.is_transitioning = False

        # Visual FX
        self.engine_flicker = 0.0

    @property
    def is_invulnerable(self) -> bool:
        """True if the player is currently in the post-hit invulnerability grace period."""
        return self.invulnerable_timer > 0.0

    @property
    def hitbox(self) -> pygame.Rect:
        """
        Hitbox slightly tighter than the sprite boundary for fair, responsive collision.
        """
        hit_w = int(self.width * 0.72)
        hit_h = int(self.height * 0.84)
        return pygame.Rect(
            int(self.x - hit_w // 2),
            int(self.y - hit_h // 2),
            hit_w,
            hit_h
        )

    def request_lane(self, desired_lane: int):
        """
        Requests a move towards desired_lane (0, 1, or 2).
        Uses sequential lane steps:
        - From 0 can step to 1.
        - From 1 can step to 0 or 2.
        - From 2 can step to 1.
        - If desired_lane requires moving through center (e.g., 0 to 2),
          it steps to lane 1 first.
        """
        desired_lane = self.lane_manager.clamp_lane(desired_lane)

        # If already at destination and not transitioning, nothing to do
        if self.current_lane == desired_lane and not self.is_transitioning:
            return

        # Next valid step according to 3-lane rules
        next_lane = self.lane_manager.next_step_toward(self.current_lane, desired_lane)

        if self.lane_manager.can_transition(self.current_lane, next_lane):
            self.target_lane = next_lane
            self.is_transitioning = True

    def move_left(self):
        """Move one lane to the left if permissible."""
        if self.current_lane > 0:
            self.request_lane(self.current_lane - 1)

    def move_right(self):
        """Move one lane to the right if permissible."""
        if self.current_lane < self.lane_manager.total_lanes - 1:
            self.request_lane(self.current_lane + 1)

    def hit(self) -> bool:
        """
        Applies damage if not invulnerable.
        Returns True if life was reduced, False if attack was blocked by invulnerability.
        """
        if self.is_invulnerable:
            return False

        self.lives = max(0, self.lives - 1)
        self.invulnerable_timer = config.INVULNERABILITY_DURATION
        return True

    def reset(self):
        """Resets the player state for a fresh game session."""
        self.current_lane = config.PLAYER_START_LANE
        self.target_lane = config.PLAYER_START_LANE
        self.x = float(self.lane_manager.get_lane_center(self.current_lane))
        self.lives = config.PLAYER_LIVES
        self.invulnerable_timer = 0.0
        self.is_transitioning = False

    def update(self, dt: float):
        """Updates car animation, lane interpolation, and invulnerability timers."""
        # Invulnerability countdown
        if self.invulnerable_timer > 0.0:
            self.invulnerable_timer = max(0.0, self.invulnerable_timer - dt)

        # Smooth lane transition that ALWAYS resolves to target lane center
        target_x = float(self.lane_manager.get_lane_center(self.target_lane))
        dist = target_x - self.x

        if abs(dist) > 0.5:
            # Snappy exponential ease-out
            self.x += dist * min(1.0, dt * config.LANE_CHANGE_LERP_SPEED)
            self.is_transitioning = True
        else:
            # Snap strictly to target lane center to guarantee exact alignment
            self.x = target_x
            self.current_lane = self.target_lane
            self.is_transitioning = False

        # Engine exhaust animation cycle
        self.engine_flicker += dt * 14.0

    def draw(self, surface: pygame.Surface):
        """Renders the player car with invulnerability flicker and exhaust effects."""
        # Check flicker during invulnerability (10 Hz blink)
        if self.is_invulnerable:
            flicker_phase = int(self.invulnerable_timer * 14.0) % 2
            if flicker_phase == 0:
                # Blink invisible frame
                return

        # Draw subtle twin exhaust flame under car
        flame_len = 8 + int(math.sin(self.engine_flicker) * 4)
        left_pipe = (int(self.x - 14), int(self.y + self.height // 2 - 4))
        right_pipe = (int(self.x + 14), int(self.y + self.height // 2 - 4))

        pygame.draw.line(surface, config.COLOR_CYAN, left_pipe, (left_pipe[0], left_pipe[1] + flame_len), 3)
        pygame.draw.line(surface, config.COLOR_CYAN, right_pipe, (right_pipe[0], right_pipe[1] + flame_len), 3)

        # Render car sprite centered at (x, y)
        draw_x = int(self.x - self.width // 2)
        draw_y = int(self.y - self.height // 2)
        surface.blit(self.sprite, (draw_x, draw_y))
