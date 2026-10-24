import sys
import time
import pygame
import config

from src.asset_manager import AssetManager
from src.lane_manager import LaneManager
from src.player import PlayerCar
from src.traffic import TrafficManager
from src.collision import CollisionManager
from src.hand_tracking import HSVHandTracker
from src.state_manager import StateManager, GameState
from src.ui import Button, UIRenderer

class Game:
    """Core Game engine class."""

    def __init__(self):
        # 1. Initialize Pygame Video & Audio
        pygame.init()
        pygame.display.set_caption(config.WINDOW_TITLE)

        self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.is_running = True

        # 2. Asset & Core Managers
        self.asset_manager = AssetManager()
        self.lane_manager = LaneManager()
        self.state_manager = StateManager(GameState.HOME)
        self.ui_renderer = UIRenderer(self.asset_manager)

        # 3. Game Entities
        player_sprite = self.asset_manager.load_image("cars/player_car.png", (config.PLAYER_WIDTH, config.PLAYER_HEIGHT))
        self.player = PlayerCar(self.lane_manager, player_sprite)

        npc_sprites = [
            self.asset_manager.load_image("cars/npc_car_01.png", (config.NPC_WIDTH, config.NPC_HEIGHT)),
            self.asset_manager.load_image("cars/npc_car_02.png", (config.NPC_WIDTH, config.NPC_HEIGHT)),
            self.asset_manager.load_image("cars/npc_car_03.png", (config.NPC_WIDTH, config.NPC_HEIGHT)),
            self.asset_manager.load_image("cars/npc_car_04.png", (config.NPC_WIDTH, config.NPC_HEIGHT))
        ]
        self.traffic_manager = TrafficManager(self.lane_manager, npc_sprites)
        self.collision_manager = CollisionManager(self.asset_manager)

        # 4. HSV Hand Tracker (Background non-blocking thread)
        self.hand_tracker = HSVHandTracker()
        self.hand_tracker.start()

        # 5. Score & Metrics
        self.score = 0
        self.survival_time = 0.0
        self.score_timer = 0.0
        self.high_score = self.asset_manager.load_high_score()
        self.current_fps = 60.0

        # 6. Interactive UI Buttons
        self._init_buttons()

    def _init_buttons(self):
        """Prepares button widgets for different screens."""
        btn_start_img = self.asset_manager.load_image("ui/start_button.png", (220, 56))
        btn_exit_img = self.asset_manager.load_image("ui/exit_button.png", (220, 56))
        btn_resume_img = self.asset_manager.load_image("ui/resume_button.png", (220, 56))
        btn_restart_img = self.asset_manager.load_image("ui/restart_button.png", (220, 56))
        btn_home_img = self.asset_manager.load_image("ui/home_button.png", (220, 56))

        # Home screen buttons
        self.home_buttons = [
            Button(config.SCREEN_WIDTH // 2 - 130, 440, btn_start_img, callback=self.start_new_game),
            Button(config.SCREEN_WIDTH // 2 + 130, 440, btn_exit_img, callback=self.quit_game)
        ]

        # Paused screen buttons
        self.paused_buttons = [
            Button(config.SCREEN_WIDTH // 2, 310, btn_resume_img, callback=self.resume_game),
            Button(config.SCREEN_WIDTH // 2, 385, btn_restart_img, callback=self.start_new_game),
            Button(config.SCREEN_WIDTH // 2, 460, btn_home_img, callback=self.go_to_home)
        ]

        # Game over buttons
        self.game_over_buttons = [
            Button(config.SCREEN_WIDTH // 2 - 130, 480, btn_restart_img, callback=self.start_new_game),
            Button(config.SCREEN_WIDTH // 2 + 130, 480, btn_home_img, callback=self.go_to_home)
        ]

    def start_new_game(self):
        """Initializes a new game run with reset stats."""
        self.player.reset()
        self.traffic_manager.reset()
        self.collision_manager.reset()
        self.score = 0
        self.survival_time = 0.0
        self.score_timer = 0.0
        self.high_score = self.asset_manager.load_high_score()
        self.state_manager.change_state(GameState.PLAYING)

    def resume_game(self):
        """Resumes active gameplay from pause."""
        self.state_manager.change_state(GameState.PLAYING)

    def go_to_home(self):
        """Navigates back to the main home screen."""
        self.state_manager.change_state(GameState.HOME)

    def quit_game(self):
        """Terminates the application cleanly."""
        self.is_running = False

    def handle_events(self):
        """Processes keyboard, mouse, and system window events."""
        mouse_pos = pygame.mouse.get_pos()
        curr_state = self.state_manager.current_state

        # Update hover states for buttons of the active screen
        active_buttons = []
        if curr_state == GameState.HOME:
            active_buttons = self.home_buttons
        elif curr_state == GameState.PAUSED:
            active_buttons = self.paused_buttons
        elif curr_state == GameState.GAME_OVER:
            active_buttons = self.game_over_buttons

        for btn in active_buttons:
            btn.update(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_game()
                return

            # Button click handling
            for btn in active_buttons:
                if btn.handle_event(event, self.asset_manager):
                    return

            # Keyboard controls
            if event.type == pygame.KEYDOWN:
                # Toggle mask debug view anytime
                if event.key == pygame.K_m:
                    self.hand_tracker.toggle_mask_mode()

                if curr_state == GameState.PLAYING:
                    # Keyboard lane steering
                    if event.key in (pygame.K_a, pygame.K_LEFT):
                        self.player.move_left()
                    elif event.key in (pygame.K_d, pygame.K_RIGHT):
                        self.player.move_right()
                    elif event.key in (pygame.K_p, pygame.K_ESCAPE):
                        self.state_manager.toggle_pause()

                elif curr_state == GameState.PAUSED:
                    if event.key in (pygame.K_p, pygame.K_ESCAPE):
                        self.state_manager.toggle_pause()

                elif curr_state == GameState.GAME_OVER:
                    if event.key == pygame.K_r:
                        self.start_new_game()
                    elif event.key == pygame.K_ESCAPE:
                        self.go_to_home()

                elif curr_state == GameState.HOME:
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.start_new_game()
                    elif event.key == pygame.K_ESCAPE:
                        self.quit_game()

    def update(self, dt: float):
        """Updates game state, tracking inputs, and entity simulations."""
        curr_state = self.state_manager.current_state

        # Hand tracking input evaluation (Always runs to keep tracker telemetry fresh)
        tracker_state = self.hand_tracker.get_state()
        if curr_state == GameState.PLAYING:
            gesture = tracker_state.get("gesture")
            if gesture == "LEFT":
                self.player.move_left()
            elif gesture == "RIGHT":
                self.player.move_right()

            # Player update
            self.player.update(dt)

            # Traffic update (returns passing bonus)
            bonus_score, passed_npcs = self.traffic_manager.update(dt, self.player.y)
            self.score += bonus_score

            # Survival time score (+10 per second)
            self.survival_time += dt
            self.score_timer += dt
            if self.score_timer >= 1.0:
                self.score += config.SCORE_PER_SECOND
                self.score_timer -= 1.0

            # Collision check
            life_lost = self.collision_manager.check_collisions(self.player, self.traffic_manager)
            if life_lost and self.player.lives <= 0:
                # Update high score and switch to GAME OVER
                if self.score > self.high_score:
                    self.high_score = self.score
                    self.asset_manager.save_high_score(self.high_score)
                self.state_manager.change_state(GameState.GAME_OVER)

            # Update particle FX and road scroll
            self.collision_manager.update(dt)
            self.ui_renderer.update_road_scroll(dt)

    def render(self):
        """Renders the current screen and components."""
        curr_state = self.state_manager.current_state
        tracker_state = self.hand_tracker.get_state()

        if curr_state in (GameState.PLAYING, GameState.PAUSED):
            # 1. Base Road Background
            road_bg = self.asset_manager.load_image("backgrounds/road_bg.png", (config.SCREEN_WIDTH, config.SCREEN_HEIGHT), use_alpha=False)
            self.screen.blit(road_bg, (0, 0))

            # 2. Animated road divider dashed lines
            self.ui_renderer.draw_road_dividers(self.screen)

            # 3. Active NPCs
            self.traffic_manager.draw(self.screen)

            # 4. Player Car
            self.player.draw(self.screen)

            # 5. Collision explosion particles
            self.collision_manager.draw(self.screen)

            # 6. Right-side System Dashboard HUD (Lives & Webcam preview only)
            self.ui_renderer.draw_dashboard_hud(
                surface=self.screen,
                lives=self.player.lives,
                tracker_state=tracker_state
            )

            # 7. Paused Screen Overlay (if paused)
            if curr_state == GameState.PAUSED:
                self.ui_renderer.draw_paused_screen(self.screen, self.paused_buttons)

        elif curr_state == GameState.HOME:
            self.ui_renderer.draw_home_screen(self.screen, self.home_buttons, self.high_score)

        elif curr_state == GameState.GAME_OVER:
            self.ui_renderer.draw_game_over_screen(self.screen, self.game_over_buttons, self.score, self.high_score)

        pygame.display.flip()

    def run(self):
        """Main game loop with fixed delta-time clamping."""
        last_time = time.time()

        try:
            while self.is_running:
                now = time.time()
                dt = now - last_time
                last_time = now

                # Clamp dt to prevent physics tunneling on lag spikes
                dt = min(dt, 0.05)

                self.handle_events()
                self.update(dt)
                self.render()

                self.clock.tick(config.FPS)
                self.current_fps = self.clock.get_fps()

        finally:
            self.cleanup()

    def cleanup(self):
        """Safely shuts down webcam thread, saves high score, and unloads Pygame."""
        print("[Game] Cleaning up resources...")
        if hasattr(self, "hand_tracker") and self.hand_tracker:
            self.hand_tracker.stop()

        if hasattr(self, "high_score"):
            self.asset_manager.save_high_score(self.high_score)

        pygame.quit()
        print("[Game] Shutdown complete.")
