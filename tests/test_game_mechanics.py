import os
import sys
import unittest
import numpy as np
import cv2
import pygame

# Set dummy headless driver for tests
os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import config
from src.lane_manager import LaneManager
from src.player import PlayerCar
from src.traffic import TrafficManager, NPC
from src.collision import CollisionManager
from src.asset_manager import AssetManager
from src.hand_tracking import HSVHandTracker

class TestLaneManager(unittest.TestCase):
    def setUp(self):
        self.lm = LaneManager([135, 305, 475])

    def test_lane_centers(self):
        self.assertEqual(self.lm.get_lane_center(0), 135)
        self.assertEqual(self.lm.get_lane_center(1), 305)
        self.assertEqual(self.lm.get_lane_center(2), 475)

    def test_lane_bounds(self):
        self.assertTrue(self.lm.is_valid_lane(0))
        self.assertTrue(self.lm.is_valid_lane(1))
        self.assertTrue(self.lm.is_valid_lane(2))
        self.assertFalse(self.lm.is_valid_lane(-1))
        self.assertFalse(self.lm.is_valid_lane(3))

    def test_transition_rules(self):
        # Lane 0 can only move to 1
        self.assertTrue(self.lm.can_transition(0, 1))
        self.assertFalse(self.lm.can_transition(0, 2))

        # Lane 1 can move to 0 or 2
        self.assertTrue(self.lm.can_transition(1, 0))
        self.assertTrue(self.lm.can_transition(1, 2))

        # Lane 2 can only move to 1
        self.assertTrue(self.lm.can_transition(2, 1))
        self.assertFalse(self.lm.can_transition(2, 0))

        # Staying in same lane is valid
        self.assertTrue(self.lm.can_transition(1, 1))

    def test_next_step_toward(self):
        # From 0 desiring 2: next step must be 1
        self.assertEqual(self.lm.next_step_toward(0, 2), 1)
        # From 2 desiring 0: next step must be 1
        self.assertEqual(self.lm.next_step_toward(2, 0), 1)
        # From 1 desiring 0: next step is 0
        self.assertEqual(self.lm.next_step_toward(1, 0), 0)
        # From 1 desiring 2: next step is 2
        self.assertEqual(self.lm.next_step_toward(1, 2), 2)


class TestPlayerCar(unittest.TestCase):
    def setUp(self):
        self.lm = LaneManager([135, 305, 475])
        dummy_surf = pygame.Surface((64, 110))
        self.player = PlayerCar(self.lm, dummy_surf)

    def test_initial_state(self):
        self.assertEqual(self.player.current_lane, 1)
        self.assertEqual(self.player.target_lane, 1)
        self.assertEqual(self.player.x, 305.0)
        self.assertEqual(self.player.lives, 3)
        self.assertFalse(self.player.is_invulnerable)

    def test_lane_transition_and_lock(self):
        # Request lane 0
        self.player.request_lane(0)
        self.assertEqual(self.player.target_lane, 0)
        self.assertTrue(self.player.is_transitioning)

        # Simulate update frames until target center reached
        for _ in range(30):
            self.player.update(0.016)

        # Must be strictly at center of Lane 0 (135.0)
        self.assertEqual(self.player.current_lane, 0)
        self.assertEqual(self.player.x, 135.0)
        self.assertFalse(self.player.is_transitioning)

    def test_lives_and_invulnerability(self):
        # First hit
        hit1 = self.player.hit()
        self.assertTrue(hit1)
        self.assertEqual(self.player.lives, 2)
        self.assertTrue(self.player.is_invulnerable)

        # Immediate second hit while invulnerable must be ignored!
        hit2 = self.player.hit()
        self.assertFalse(hit2)
        self.assertEqual(self.player.lives, 2)

        # Advance time past invulnerability period (1.3s)
        self.player.update(1.4)
        self.assertFalse(self.player.is_invulnerable)

        # Hit again
        hit3 = self.player.hit()
        self.assertTrue(hit3)
        self.assertEqual(self.player.lives, 1)


class TestTrafficAndFairSpawn(unittest.TestCase):
    def setUp(self):
        self.lm = LaneManager([135, 305, 475])
        dummy_surf = pygame.Surface((64, 110))
        self.tm = TrafficManager(self.lm, [dummy_surf])

    def test_no_all_three_lanes_blocked(self):
        # Force simulate spawning multiple waves
        for _ in range(50):
            self.tm.spawn_timer = 2.0
            self.tm.update(0.1, player_y=560.0)

            # Check that in the upper threat area (y < 280), not all 3 lanes are blocked
            lanes_occupied = set(npc.lane for npc in self.tm.npcs if npc.y < 280.0)
            self.assertLess(len(lanes_occupied), 3, "Fairness violation: All 3 lanes were blocked simultaneously!")

    def test_passing_bonus_score(self):
        # Place an NPC above player
        dummy_surf = pygame.Surface((64, 110))
        npc = NPC(lane=0, x=135.0, y=400.0, speed=200.0, sprite=dummy_surf, car_type=0)
        self.tm.npcs.append(npc)

        player_y = 560.0
        # NPC has not passed player yet
        bonus, passed = self.tm.update(0.01, player_y)
        self.assertEqual(bonus, 0)

        # Move NPC past player
        npc.y = 650.0
        bonus, passed = self.tm.update(0.01, player_y)
        self.assertEqual(bonus, config.SCORE_PER_PASS)
        self.assertTrue(npc.passed)

        # Next frame: must not award bonus again!
        bonus2, passed2 = self.tm.update(0.01, player_y)
        self.assertEqual(bonus2, 0)


class TestCollisionManager(unittest.TestCase):
    def setUp(self):
        self.am = AssetManager()
        self.lm = LaneManager([135, 305, 475])
        dummy_surf = pygame.Surface((64, 110))
        self.player = PlayerCar(self.lm, dummy_surf)
        self.tm = TrafficManager(self.lm, [dummy_surf])
        self.cm = CollisionManager(self.am)

    def test_collision_reduces_exactly_one_life(self):
        # Spawn NPC directly at player position
        npc = NPC(lane=1, x=self.player.x, y=self.player.y, speed=0.0, sprite=self.player.sprite, car_type=0)
        self.tm.npcs.append(npc)

        # Collision check
        life_lost = self.cm.check_collisions(self.player, self.tm)
        self.assertTrue(life_lost)
        self.assertEqual(self.player.lives, 2)
        self.assertTrue(self.player.is_invulnerable)
        # NPC must be deactivated
        self.assertFalse(npc.active)

        # Next check should NOT reduce life because player is invulnerable
        life_lost2 = self.cm.check_collisions(self.player, self.tm)
        self.assertFalse(life_lost2)
        self.assertEqual(self.player.lives, 2)


class TestHSVColorTrackingLogic(unittest.TestCase):
    def setUp(self):
        self.tracker = HSVHandTracker()

    def test_motion_gesture_detection(self):
        now = 100.0
        # 1. Initial detection sets baseline
        res1 = self.tracker.process_motion(150.0, now)
        self.assertIsNone(res1)
        self.assertEqual(self.tracker.baseline_x, 150.0)

        # 2. Small movement (e.g. +10px) -> No trigger
        res2 = self.tracker.process_motion(160.0, now + 0.05)
        self.assertIsNone(res2)

        # 3. Intentional move to the RIGHT (+45px from baseline) -> Triggers "RIGHT"
        res3 = self.tracker.process_motion(200.0, now + 0.1)
        self.assertEqual(res3, "RIGHT")

        # 4. Immediate subsequent movement during cooldown -> Must be ignored!
        res4 = self.tracker.process_motion(250.0, now + 0.15)
        self.assertIsNone(res4)

        # 5. After cooldown (e.g. +0.5s later), moving LEFT -> Triggers "LEFT"
        now2 = now + 0.6
        # Set new baseline position
        self.tracker.process_motion(200.0, now2)
        # Move left by -50px
        res5 = self.tracker.process_motion(140.0, now2 + 0.05)
        self.assertEqual(res5, "LEFT")

    def test_blue_segmentation_with_synthetic_frame(self):
        # Create a synthetic 320x240 image with a vibrant blue card placed at (x=240, y=120)
        img = np.zeros((240, 320, 3), dtype=np.uint8)
        # Pure blue rectangle: in BGR, (B=230, G=40, R=10)
        cv2.rectangle(img, (210, 80), (270, 160), (230, 40, 10), -1)

        # Convert to HSV
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, config.LOWER_BLUE, config.UPPER_BLUE)

        # Morphological clean
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        mask_clean = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask_clean = cv2.morphologyEx(mask_clean, cv2.MORPH_CLOSE, kernel)

        # Find contours
        contours, _ = cv2.findContours(mask_clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        self.assertTrue(len(contours) > 0)

        cnt = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(cnt)
        self.assertGreater(area, 1000)

        # Calculate centroid moments
        M = cv2.moments(cnt)
        self.assertGreater(M["m00"], 0)
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])

        # Expected centroid: x = 240, y = 120
        self.assertAlmostEqual(cx, 240, delta=2)
        self.assertAlmostEqual(cy, 120, delta=2)


if __name__ == "__main__":
    unittest.main()
