import os
import sys
import unittest
import pygame

# Set dummy headless driver
os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.game import Game
from src.state_manager import GameState

class TestGameIntegration(unittest.TestCase):
    def setUp(self):
        self.game = Game()

    def tearDown(self):
        self.game.cleanup()

    def test_full_state_lifecycle(self):
        # 1. Starts in HOME state
        self.assertEqual(self.game.state_manager.current_state, GameState.HOME)

        # Render home screen
        self.game.render()

        # 2. Transition to PLAYING
        self.game.start_new_game()
        self.assertEqual(self.game.state_manager.current_state, GameState.PLAYING)
        self.assertEqual(self.game.player.lives, 3)
        self.assertEqual(self.game.score, 0)

        # Simulate 20 game loop update + render ticks
        for _ in range(20):
            self.game.update(0.016)
            self.game.render()

        # Simulate keyboard movement to left
        self.game.player.move_left()
        self.assertEqual(self.game.player.target_lane, 0)
        for _ in range(25):
            self.game.update(0.016)
        self.assertEqual(self.game.player.current_lane, 0)

        # Simulate keyboard movement to right
        self.game.player.move_right()
        self.assertEqual(self.game.player.target_lane, 1)
        for _ in range(25):
            self.game.update(0.016)
        self.assertEqual(self.game.player.current_lane, 1)

        # 3. Transition to PAUSED
        self.game.state_manager.toggle_pause()
        self.assertEqual(self.game.state_manager.current_state, GameState.PAUSED)
        self.game.render()

        # Resume
        self.game.resume_game()
        self.assertEqual(self.game.state_manager.current_state, GameState.PLAYING)

        # 4. Trigger GAME_OVER by depleting lives
        self.game.player.lives = 0
        self.game.state_manager.change_state(GameState.GAME_OVER)
        self.assertEqual(self.game.state_manager.current_state, GameState.GAME_OVER)
        self.game.render()

        # 5. Restart from GAME_OVER
        self.game.start_new_game()
        self.assertEqual(self.game.state_manager.current_state, GameState.PLAYING)
        self.assertEqual(self.game.player.lives, 3)

        # 6. Return to HOME
        self.game.go_to_home()
        self.assertEqual(self.game.state_manager.current_state, GameState.HOME)
        self.game.render()

if __name__ == "__main__":
    unittest.main()
