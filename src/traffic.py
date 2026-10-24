import random
from typing import List, Tuple
import pygame
import config
from src.lane_manager import LaneManager

class NPC:
    """Represents an individual NPC obstacle car."""

    def __init__(self, lane: int, x: float, y: float, speed: float, sprite: pygame.Surface, car_type: int):
        self.lane = lane
        self.x = x
        self.y = y
        self.speed = speed
        self.sprite = sprite
        self.car_type = car_type

        self.width = config.NPC_WIDTH
        self.height = config.NPC_HEIGHT

        self.active = True
        self.passed = False  # Track whether player safely passed this car

    @property
    def hitbox(self) -> pygame.Rect:
        """Slightly tightened collision box for fair gameplay."""
        hit_w = int(self.width * 0.72)
        hit_h = int(self.height * 0.84)
        return pygame.Rect(
            int(self.x - hit_w // 2),
            int(self.y - hit_h // 2),
            hit_w,
            hit_h
        )

    def update(self, dt: float, road_scroll_speed: float):
        """Moves NPC car downward relative to the road."""
        self.y += (self.speed + road_scroll_speed * 0.3) * dt

        # Deactivate when far below screen
        if self.y > config.SCREEN_HEIGHT + 120:
            self.active = False

    def draw(self, surface: pygame.Surface):
        """Renders NPC sprite centered at (x, y)."""
        draw_x = int(self.x - self.width // 2)
        draw_y = int(self.y - self.height // 2)
        surface.blit(self.sprite, (draw_x, draw_y))


class TrafficManager:
    """
    Spawns and manages NPC vehicles with dynamic difficulty scaling
    and fairness algorithms.
    """

    def __init__(self, lane_manager: LaneManager, npc_sprites: List[pygame.Surface]):
        self.lane_manager = lane_manager
        self.npc_sprites = npc_sprites
        self.npcs: List[NPC] = []

        # Difficulty & Spawn timers
        self.spawn_timer = 0.0
        self.elapsed_time = 0.0
        self.difficulty_level = 1

    def reset(self):
        """Clears all traffic and resets timers."""
        self.npcs.clear()
        self.spawn_timer = 0.0
        self.elapsed_time = 0.0
        self.difficulty_level = 1

    @property
    def current_spawn_interval(self) -> float:
        """Calculates dynamic spawn interval based on difficulty level."""
        interval = config.BASE_SPAWN_INTERVAL - (self.difficulty_level - 1) * 0.1
        return max(config.MIN_SPAWN_INTERVAL, interval)

    @property
    def current_npc_speed(self) -> float:
        """Calculates current base speed for newly spawned NPCs."""
        speed = config.BASE_NPC_SPEED + (self.difficulty_level - 1) * 35.0
        return min(config.MAX_NPC_SPEED, speed)

    def _get_occupied_lanes_near_top(self, threshold_y: float = 240.0) -> List[int]:
        """Finds lanes that currently have a car within threshold_y from top."""
        occupied = set()
        for npc in self.npcs:
            if npc.y < threshold_y:
                occupied.add(npc.lane)
        return list(occupied)

    def _can_spawn_in_lane(self, lane_idx: int) -> bool:
        """Checks if a lane has sufficient vertical clearance for a new car."""
        for npc in self.npcs:
            if npc.lane == lane_idx:
                # Must be at least MIN_NPC_VERTICAL_GAP pixels away from top (-100)
                if abs(npc.y - (-100.0)) < config.MIN_NPC_VERTICAL_GAP:
                    return False
        return True

    def spawn_npc(self):
        """
        Spawns an NPC using fairness rules:
        1. Checks occupied lanes near the top.
        2. Never blocks all 3 lanes simultaneously (always ensures an open escape lane).
        3. Enforces vertical gaps between consecutive cars in the same lane.
        """
        if len(self.npcs) >= config.MAX_ACTIVE_NPCS:
            return

        occupied_near_top = self._get_occupied_lanes_near_top(threshold_y=280.0)

        # Candidates are lanes that:
        # a) have sufficient vertical clearance
        # b) will not cause all 3 lanes to be blocked simultaneously
        candidate_lanes = []
        for lane in range(self.lane_manager.total_lanes):
            if self._can_spawn_in_lane(lane):
                # If adding this lane would block all 3 lanes at the top, skip it
                potential_blocked = set(occupied_near_top).union({lane})
                if len(potential_blocked) < self.lane_manager.total_lanes:
                    candidate_lanes.append(lane)

        if not candidate_lanes:
            return

        chosen_lane = random.choice(candidate_lanes)
        lane_center_x = float(self.lane_manager.get_lane_center(chosen_lane))

        # Random car visual variant
        car_type = random.randint(0, len(self.npc_sprites) - 1)
        sprite = self.npc_sprites[car_type]

        # Slight speed variation (+/- 10%) per car
        speed_variation = random.uniform(0.92, 1.08)
        car_speed = self.current_npc_speed * speed_variation

        spawn_y = -float(config.NPC_HEIGHT) - random.uniform(10.0, 40.0)

        new_npc = NPC(
            lane=chosen_lane,
            x=lane_center_x,
            y=spawn_y,
            speed=car_speed,
            sprite=sprite,
            car_type=car_type
        )
        self.npcs.append(new_npc)

    def update(self, dt: float, player_y: float) -> Tuple[int, List[NPC]]:
        """
        Updates all NPC positions, handles spawning, difficulty progression,
        and awards passing scores.
        Returns:
            (bonus_score, newly_passed_npcs)
        """
        self.elapsed_time += dt
        self.spawn_timer += dt

        # Ramp difficulty every DIFFICULTY_RAMP_INTERVAL seconds
        self.difficulty_level = 1 + int(self.elapsed_time / config.DIFFICULTY_RAMP_INTERVAL)

        # Trigger spawn if timer exceeds current dynamic interval
        if self.spawn_timer >= self.current_spawn_interval:
            self.spawn_npc()
            self.spawn_timer = 0.0

        bonus_score = 0
        passed_npcs = []

        # Update all active NPCs
        for npc in self.npcs:
            npc.update(dt, config.SCROLL_SPEED)

            # Check if player safely passed this NPC
            if not npc.passed and npc.y > player_y + config.NPC_HEIGHT // 2:
                npc.passed = True
                bonus_score += config.SCORE_PER_PASS
                passed_npcs.append(npc)

        # Purge inactive NPCs that left the screen
        self.npcs = [npc for npc in self.npcs if npc.active]

        return bonus_score, passed_npcs

    def draw(self, surface: pygame.Surface):
        """Draws all active NPCs."""
        for npc in self.npcs:
            npc.draw(surface)
