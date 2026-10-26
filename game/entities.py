# Game entities for Hand Tracking Car Game:
# - LaneManager: Controls the 3 fixed road lanes and strict boundary locking.
# - PlayerCar: Player vehicle with smooth lane interpolation, invulnerability, and lives.
# - NPC: Oncoming obstacle cars with varying sprites and fair hitboxes.
# - TrafficManager: Spawns NPCs fairly (never 3 blocked lanes) and handles difficulty progression.

import math
import random
from typing import List, Tuple
import pygame
from game import config

class LaneManager:
    # Manages the 3 fixed lanes, their screen coordinates, and transition validity

    def __init__(self, lane_centers=None):
        if lane_centers is None:
            self.lane_centers = list(config.LANE_CENTERS)
        else:
            self.lane_centers = list(lane_centers)
        self.total_lanes = len(self.lane_centers)

    def get_lane_center(self, lane_idx: int) -> int:
        # Returns horizontal center coordinate (x) for given lane index
        clamped = self.clamp_lane(lane_idx)
        return self.lane_centers[clamped]

    def is_valid_lane(self, lane_idx: int) -> bool:
        # Checks if a lane index is within valid bounds [0, 2]
        return 0 <= lane_idx < self.total_lanes

    def clamp_lane(self, lane_idx: int) -> int:
        # Restricts lane index strictly within [0, total_lanes - 1]
        return max(0, min(self.total_lanes - 1, int(lane_idx)))

    def can_transition(self, from_lane: int, to_lane: int) -> bool:
        # Validates 1-step atomic transition between adjacent lanes
        if not self.is_valid_lane(from_lane) or not self.is_valid_lane(to_lane):
            return False
        if from_lane == to_lane:
            return True
        return abs(to_lane - from_lane) == 1

    def next_step_toward(self, current_lane: int, target_lane: int) -> int:
        # Determines next sequential lane step
        target = self.clamp_lane(target_lane)
        current = self.clamp_lane(current_lane)
        if target > current:
            return current + 1
        elif target < current:
            return current - 1
        return current


class PlayerCar:
    # Represents player-controlled car

    def __init__(self, lane_manager: LaneManager, sprite: pygame.Surface):
        self.lane_manager = lane_manager
        self.sprite = sprite

        self.current_lane = config.PLAYER_START_LANE
        self.target_lane = config.PLAYER_START_LANE

        # Fixed vertical position (bottom of road)
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
        # True if player is in invulnerability period
        return self.invulnerable_timer > 0.0

    @property
    def hitbox(self) -> pygame.Rect:
        # Hitbox slightly tighter than sprite boundary for fair collision
        hit_w = int(self.width * 0.72)
        hit_h = int(self.height * 0.84)
        return pygame.Rect(
            int(self.x - hit_w // 2),
            int(self.y - hit_h // 2),
            hit_w,
            hit_h
        )

    def request_lane(self, desired_lane: int):
        # Requests moving towards desired_lane sequentially
        desired_lane = self.lane_manager.clamp_lane(desired_lane)
        if self.current_lane == desired_lane and not self.is_transitioning:
            return

        next_lane = self.lane_manager.next_step_toward(self.current_lane, desired_lane)
        if self.lane_manager.can_transition(self.current_lane, next_lane):
            self.target_lane = next_lane
            self.is_transitioning = True

    def move_left(self):
        # Shift one lane to the left
        if self.current_lane > 0:
            self.request_lane(self.current_lane - 1)

    def move_right(self):
        # Shift one lane to the right
        if self.current_lane < self.lane_manager.total_lanes - 1:
            self.request_lane(self.current_lane + 1)

    def hit(self) -> bool:
        # Deducts one life if not invulnerable
        if self.is_invulnerable:
            return False

        self.lives = max(0, self.lives - 1)
        self.invulnerable_timer = config.INVULNERABILITY_DURATION
        return True

    def reset(self):
        # Resets player state for a fresh game session
        self.current_lane = config.PLAYER_START_LANE
        self.target_lane = config.PLAYER_START_LANE
        self.x = float(self.lane_manager.get_lane_center(self.current_lane))
        self.lives = config.PLAYER_LIVES
        self.invulnerable_timer = 0.0
        self.is_transitioning = False

    def update(self, dt: float):
        # Updates car animation and lane interpolation
        if self.invulnerable_timer > 0.0:
            self.invulnerable_timer = max(0.0, self.invulnerable_timer - dt)

        target_x = float(self.lane_manager.get_lane_center(self.target_lane))
        dist = target_x - self.x

        if abs(dist) > 0.5:
            self.x += dist * min(1.0, dt * config.LANE_CHANGE_LERP_SPEED)
            self.is_transitioning = True
        else:
            self.x = target_x
            self.current_lane = self.target_lane
            self.is_transitioning = False

        self.engine_flicker += dt * 14.0

    def draw(self, surface: pygame.Surface):
        # Renders player car with invulnerability flicker
        if self.is_invulnerable:
            flicker_phase = int(self.invulnerable_timer * 14.0) % 2
            if flicker_phase == 0:
                return

        flame_len = 8 + int(math.sin(self.engine_flicker) * 4)
        left_pipe = (int(self.x - 14), int(self.y + self.height // 2 - 4))
        right_pipe = (int(self.x + 14), int(self.y + self.height // 2 - 4))

        pygame.draw.line(surface, config.COLOR_CYAN, left_pipe, (left_pipe[0], left_pipe[1] + flame_len), 3)
        pygame.draw.line(surface, config.COLOR_CYAN, right_pipe, (right_pipe[0], right_pipe[1] + flame_len), 3)

        draw_x = int(self.x - self.width // 2)
        draw_y = int(self.y - self.height // 2)
        surface.blit(self.sprite, (draw_x, draw_y))


class NPC:
    # Represents obstacle vehicle

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
        self.passed = False

    @property
    def hitbox(self) -> pygame.Rect:
        # Collision hitbox tighter than sprite boundary
        hit_w = int(self.width * 0.72)
        hit_h = int(self.height * 0.84)
        return pygame.Rect(
            int(self.x - hit_w // 2),
            int(self.y - hit_h // 2),
            hit_w,
            hit_h
        )

    def update(self, dt: float, road_scroll_speed: float):
        # Moves NPC car downward
        self.y += (self.speed + road_scroll_speed * 0.3) * dt
        if self.y > config.SCREEN_HEIGHT + 120:
            self.active = False

    def draw(self, surface: pygame.Surface):
        # Renders NPC sprite
        draw_x = int(self.x - self.width // 2)
        draw_y = int(self.y - self.height // 2)
        surface.blit(self.sprite, (draw_x, draw_y))


class TrafficManager:
    # Manages procedural NPC spawning and dynamic difficulty

    def __init__(self, lane_manager: LaneManager, npc_sprites: List[pygame.Surface]):
        self.lane_manager = lane_manager
        self.npc_sprites = npc_sprites
        self.npcs: List[NPC] = []

        self.spawn_timer = 0.0
        self.elapsed_time = 0.0
        self.difficulty_level = 1

    def reset(self):
        # Clears all traffic and resets timers
        self.npcs.clear()
        self.spawn_timer = 0.0
        self.elapsed_time = 0.0
        self.difficulty_level = 1

    @property
    def current_spawn_interval(self) -> float:
        # Calculates dynamic spawn interval based on difficulty level
        interval = config.BASE_SPAWN_INTERVAL - (self.difficulty_level - 1) * 0.1
        return max(config.MIN_SPAWN_INTERVAL, interval)

    @property
    def current_npc_speed(self) -> float:
        # Calculates base speed for newly spawned NPCs
        speed = config.BASE_NPC_SPEED + (self.difficulty_level - 1) * 35.0
        return min(config.MAX_NPC_SPEED, speed)

    def _get_occupied_lanes_near_top(self, threshold_y: float = 240.0) -> List[int]:
        # Finds lanes that currently have a car within threshold_y from top
        occupied = set()
        for npc in self.npcs:
            if npc.y < threshold_y:
                occupied.add(npc.lane)
        return list(occupied)

    def _can_spawn_in_lane(self, lane_idx: int) -> bool:
        # Checks if a lane has sufficient vertical clearance
        for npc in self.npcs:
            if npc.lane == lane_idx:
                if abs(npc.y - (-100.0)) < config.MIN_NPC_VERTICAL_GAP:
                    return False
        return True

    def spawn_npc(self):
        # Spawns NPC using fairness rules
        if len(self.npcs) >= config.MAX_ACTIVE_NPCS:
            return

        occupied_near_top = self._get_occupied_lanes_near_top(threshold_y=280.0)

        candidate_lanes = []
        for lane in range(self.lane_manager.total_lanes):
            if self._can_spawn_in_lane(lane):
                potential_blocked = set(occupied_near_top).union({lane})
                # Never block all lanes simultaneously
                if len(potential_blocked) < self.lane_manager.total_lanes:
                    candidate_lanes.append(lane)

        if not candidate_lanes:
            return

        chosen_lane = random.choice(candidate_lanes)
        lane_center_x = float(self.lane_manager.get_lane_center(chosen_lane))

        car_type = random.randint(0, len(self.npc_sprites) - 1)
        sprite = self.npc_sprites[car_type]

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
        # Updates all NPCs and awards passing bonus scores
        self.elapsed_time += dt
        self.spawn_timer += dt

        self.difficulty_level = 1 + int(self.elapsed_time / config.DIFFICULTY_RAMP_INTERVAL)

        if self.spawn_timer >= self.current_spawn_interval:
            self.spawn_npc()
            self.spawn_timer = 0.0

        bonus_score = 0
        passed_npcs = []

        for npc in self.npcs:
            npc.update(dt, config.SCROLL_SPEED)
            if not npc.passed and npc.y > player_y + config.NPC_HEIGHT // 2:
                npc.passed = True
                bonus_score += config.SCORE_PER_PASS
                passed_npcs.append(npc)

        self.npcs = [npc for npc in self.npcs if npc.active]
        return bonus_score, passed_npcs

    def draw(self, surface: pygame.Surface):
        # Draws all active NPCs
        for npc in self.npcs:
            npc.draw(surface)
