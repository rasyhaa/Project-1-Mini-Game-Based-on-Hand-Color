import sys
import time
from enum import Enum, auto
from typing import Optional, Tuple, Callable
import pygame
from game import config
from game.assets import AssetManager
from game.entities import LaneManager, PlayerCar, TrafficManager
from game.particles import CollisionManager
from game.camera import HSVHandTracker

class GameState(Enum):
    # Game state machine states
    HOME = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()


class Button:

    def __init__(self, x: int, y: int, image: pygame.Surface, callback: Optional[Callable] = None):
        self.normal_image = image
        self.rect = self.normal_image.get_rect(center=(x, y))
        self.callback = callback
        self.is_hovered = False

        w, h = self.normal_image.get_size()
        self.hover_image = pygame.Surface((w, h), pygame.SRCALPHA)
        self.hover_image.blit(self.normal_image, (0, 0))
        pygame.draw.rect(self.hover_image, config.COLOR_CYAN, (0, 0, w, h), width=3, border_radius=14)

    def update(self, mouse_pos: Tuple[int, int]):
        # Updates hover status
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def handle_event(self, event: pygame.event.Event) -> bool:
        # Processes mouse clicks and triggers callback
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.callback:
                    self.callback()
                return True
        return False

    def draw(self, surface: pygame.Surface):
        # Draws button in current state
        img = self.hover_image if self.is_hovered else self.normal_image
        surface.blit(img, self.rect.topleft)


class Game:

    def __init__(self):
        pygame.init()
        pygame.display.set_caption(config.WINDOW_TITLE)

        self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.is_running = True

        self.state = GameState.HOME

        # Asset & entity managers
        self.asset_manager = AssetManager()
        self.lane_manager = LaneManager()

        player_sprite = self.asset_manager.load_image("cars/player_car.png", (config.PLAYER_WIDTH, config.PLAYER_HEIGHT))
        self.player = PlayerCar(self.lane_manager, player_sprite)

        npc_sprites = [
            self.asset_manager.load_image("cars/npc_car_01.png", (config.NPC_WIDTH, config.NPC_HEIGHT)),
            self.asset_manager.load_image("cars/npc_car_02.png", (config.NPC_WIDTH, config.NPC_HEIGHT)),
            self.asset_manager.load_image("cars/npc_car_03.png", (config.NPC_WIDTH, config.NPC_HEIGHT)),
            self.asset_manager.load_image("cars/npc_car_04.png", (config.NPC_WIDTH, config.NPC_HEIGHT))
        ]
        self.traffic_manager = TrafficManager(self.lane_manager, npc_sprites)
        self.collision_manager = CollisionManager()

        # HSV camera tracker
        self.hand_tracker = HSVHandTracker()
        self.hand_tracker.start()

        # Metrics & scores
        self.score = 0
        self.survival_time = 0.0
        self.score_timer = 0.0
        self.high_score = self.asset_manager.load_high_score()
        self.current_fps = 60.0

        # Road animation scroll offset
        self.road_scroll_offset = 0.0

        self._init_buttons()

    def _init_buttons(self):
        # Prepares buttons for all screens
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
        # Resets all metrics and launches a new gameplay session
        self.player.reset()
        self.traffic_manager.reset()
        self.collision_manager.reset()
        self.score = 0
        self.survival_time = 0.0
        self.score_timer = 0.0
        self.high_score = self.asset_manager.load_high_score()
        self.state = GameState.PLAYING

    def resume_game(self):
        # Resumes active gameplay from pause
        self.state = GameState.PLAYING

    def go_to_home(self):
        # Navigates to Home screen
        self.state = GameState.HOME

    def toggle_pause(self):
        # Toggles between PLAYING and PAUSED
        if self.state == GameState.PLAYING:
            self.state = GameState.PAUSED
        elif self.state == GameState.PAUSED:
            self.state = GameState.PLAYING

    def quit_game(self):
        # Terminates the application
        self.is_running = False

    def handle_events(self):
        # Processes keyboard, mouse, and system events
        mouse_pos = pygame.mouse.get_pos()

        active_buttons = []
        if self.state == GameState.HOME:
            active_buttons = self.home_buttons
        elif self.state == GameState.PAUSED:
            active_buttons = self.paused_buttons
        elif self.state == GameState.GAME_OVER:
            active_buttons = self.game_over_buttons

        for btn in active_buttons:
            btn.update(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_game()
                return

            for btn in active_buttons:
                if btn.handle_event(event):
                    return

            if event.type == pygame.KEYDOWN:
                if self.state == GameState.PLAYING:
                    if event.key in (pygame.K_a, pygame.K_LEFT):
                        self.player.move_left()
                    elif event.key in (pygame.K_d, pygame.K_RIGHT):
                        self.player.move_right()
                    elif event.key in (pygame.K_p, pygame.K_ESCAPE):
                        self.toggle_pause()

                elif self.state == GameState.PAUSED:
                    if event.key in (pygame.K_p, pygame.K_ESCAPE):
                        self.toggle_pause()

                elif self.state == GameState.GAME_OVER:
                    if event.key == pygame.K_r:
                        self.start_new_game()
                    elif event.key == pygame.K_ESCAPE:
                        self.go_to_home()

                elif self.state == GameState.HOME:
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.start_new_game()
                    elif event.key == pygame.K_ESCAPE:
                        self.quit_game()

    def update(self, dt: float):
        # Updates game state, camera input, and entities
        tracker_state = self.hand_tracker.get_state()

        if self.state == GameState.PLAYING:
            gesture = tracker_state.get("gesture")
            if gesture == "LEFT":
                self.player.move_left()
            elif gesture == "RIGHT":
                self.player.move_right()

            self.player.update(dt)

            bonus_score, passed_npcs = self.traffic_manager.update(dt, self.player.y)
            self.score += bonus_score

            self.survival_time += dt
            self.score_timer += dt
            if self.score_timer >= 1.0:
                self.score += config.SCORE_PER_SECOND
                self.score_timer -= 1.0

            life_lost = self.collision_manager.check_collisions(self.player, self.traffic_manager)
            if life_lost and self.player.lives <= 0:
                if self.score > self.high_score:
                    self.high_score = self.score
                    self.asset_manager.save_high_score(self.high_score)
                self.state = GameState.GAME_OVER

            self.collision_manager.update(dt)
            self.road_scroll_offset = (self.road_scroll_offset + config.SCROLL_SPEED * dt) % 60.0

    def draw_road_dividers(self, surface: pygame.Surface):
        # Draws animated dashed road dividing lines
        dash_len = 35
        gap_len = 25
        cycle = dash_len + gap_len

        for base_y in range(-cycle, config.SCREEN_HEIGHT + cycle, cycle):
            y = base_y + int(self.road_scroll_offset)
            pygame.draw.line(surface, config.COLOR_WHITE, (220, y), (220, y + dash_len), 4)
            pygame.draw.line(surface, config.COLOR_WHITE, (390, y), (390, y + dash_len), 4)

    def draw_dashboard_hud(self, surface: pygame.Surface, tracker_state: dict):
        # Renders the right-side dashboard (x = 600 to 1000)
        # Contains ONLY: Lives (heart icons) and clean Webcam preview feed
        font_body = self.asset_manager.get_font("body")
        dash_x = config.DASHBOARD_X
        center_x = dash_x + config.DASHBOARD_WIDTH // 2

        # 1. Lives Display (Nyawa)
        heart_full = self.asset_manager.load_image("ui/heart_full.png", (38, 38))
        heart_empty = self.asset_manager.load_image("ui/heart_empty.png", (38, 38))

        lives_label = font_body.render("LIVES:", True, config.COLOR_WHITE)
        total_lives_width = lives_label.get_width() + 15 + (config.PLAYER_LIVES * 44)
        start_x = center_x - total_lives_width // 2
        lives_y = 65

        surface.blit(lives_label, (start_x, lives_y + 4))
        for i in range(config.PLAYER_LIVES):
            h_img = heart_full if i < self.player.lives else heart_empty
            surface.blit(h_img, (start_x + lives_label.get_width() + 15 + i * 44, lives_y))

        # 2. Webcam Feed Container (Tampilan Webcam)
        cam_x = center_x - config.WEBCAM_FRAME_WIDTH // 2
        cam_y = 160
        cam_w = config.WEBCAM_FRAME_WIDTH
        cam_h = config.WEBCAM_FRAME_HEIGHT

        feed_rect = pygame.Rect(cam_x - 3, cam_y - 3, cam_w + 6, cam_h + 6)
        pygame.draw.rect(surface, (0, 180, 240), feed_rect, 2, border_radius=8)

        cam_available = tracker_state.get("is_camera_available", False)
        preview_surf = tracker_state.get("preview_surface")

        if cam_available and preview_surf is not None:
            surface.blit(preview_surf, (cam_x, cam_y))
        else:
            placeholder = pygame.Surface((cam_w, cam_h))
            placeholder.fill((20, 24, 32))
            no_cam_txt = font_body.render("WEBCAM OFFLINE", True, config.COLOR_RED)
            placeholder.blit(no_cam_txt, no_cam_txt.get_rect(center=(cam_w // 2, cam_h // 2)))
            surface.blit(placeholder, (cam_x, cam_y))

    def draw_home_screen(self, surface: pygame.Surface):
        # Renders Home Screen menu
        home_bg = self.asset_manager.load_image("backgrounds/home_bg.png", (config.SCREEN_WIDTH, config.SCREEN_HEIGHT), use_alpha=False)
        surface.blit(home_bg, (0, 0))

        font_title = self.asset_manager.get_font("title")
        font_header = self.asset_manager.get_font("header")

        # Title shadow & glow
        title_str = "Hand Tracking Car Game"
        t_shadow = font_title.render(title_str, True, (0, 30, 60))
        t_glow = font_title.render(title_str, True, config.COLOR_CYAN)
        surface.blit(t_shadow, (config.SCREEN_WIDTH // 2 - t_shadow.get_width() // 2 + 2, 72))
        surface.blit(t_glow, (config.SCREEN_WIDTH // 2 - t_glow.get_width() // 2, 70))

        # High score banner
        hs_str = f"HIGH SCORE: {self.high_score:06d}"
        hs_surf = font_header.render(hs_str, True, config.COLOR_WHITE)
        surface.blit(hs_surf, (config.SCREEN_WIDTH // 2 - hs_surf.get_width() // 2, 140))

        # Showcase player car in center
        player_car = self.asset_manager.load_image("cars/player_car.png", (84, 144))
        surface.blit(player_car, (config.SCREEN_WIDTH // 2 - 42, 215))

        # Draw buttons
        for btn in self.home_buttons:
            btn.draw(surface)

    def draw_paused_screen(self, surface: pygame.Surface):
        # Draws pause overlay
        dim_surf = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
        dim_surf.fill((10, 15, 22, 200))
        surface.blit(dim_surf, (0, 0))

        font_title = self.asset_manager.get_font("title")
        p_txt = font_title.render("GAME PAUSED", True, config.COLOR_CYAN)
        surface.blit(p_txt, p_txt.get_rect(center=(config.SCREEN_WIDTH // 2, 220)))

        for btn in self.paused_buttons:
            btn.draw(surface)

    def draw_game_over_screen(self, surface: pygame.Surface):
        # Renders Game Over screen
        bg = self.asset_manager.load_image("backgrounds/game_over_bg.png", (config.SCREEN_WIDTH, config.SCREEN_HEIGHT), use_alpha=False)
        surface.blit(bg, (0, 0))

        font_title = self.asset_manager.get_font("title")
        font_header = self.asset_manager.get_font("header")
        font_body = self.asset_manager.get_font("body")

        go_txt = font_title.render("GAME OVER", True, config.COLOR_RED)
        surface.blit(go_txt, go_txt.get_rect(center=(config.SCREEN_WIDTH // 2, 160)))

        box_rect = pygame.Rect(config.SCREEN_WIDTH // 2 - 200, 240, 400, 160)
        box_surf = pygame.Surface((400, 160), pygame.SRCALPHA)
        box_surf.fill((20, 24, 34, 220))
        pygame.draw.rect(box_surf, config.COLOR_RED, (0, 0, 400, 160), width=2, border_radius=12)
        surface.blit(box_surf, box_rect.topleft)

        score_txt = font_header.render(f"FINAL SCORE: {self.score:06d}", True, config.COLOR_YELLOW)
        high_txt = font_body.render(f"HIGH SCORE:  {self.high_score:06d}", True, config.COLOR_WHITE)

        is_new_best = self.score >= self.high_score and self.score > 0
        tag_str = "★ NEW HIGH SCORE! ★" if is_new_best else "BETTER LUCK NEXT RUN!"
        tag_color = config.COLOR_GREEN if is_new_best else config.COLOR_GRAY_LIGHT
        tag_surf = font_body.render(tag_str, True, tag_color)

        surface.blit(score_txt, score_txt.get_rect(center=(config.SCREEN_WIDTH // 2, 280)))
        surface.blit(high_txt, high_txt.get_rect(center=(config.SCREEN_WIDTH // 2, 325)))
        surface.blit(tag_surf, tag_surf.get_rect(center=(config.SCREEN_WIDTH // 2, 365)))

        for btn in self.game_over_buttons:
            btn.draw(surface)

    def render(self):
        # Renders game visuals based on current state
        tracker_state = self.hand_tracker.get_state()

        if self.state in (GameState.PLAYING, GameState.PAUSED):
            road_bg = self.asset_manager.load_image("backgrounds/road_bg.png", (config.SCREEN_WIDTH, config.SCREEN_HEIGHT), use_alpha=False)
            self.screen.blit(road_bg, (0, 0))

            self.draw_road_dividers(self.screen)
            self.traffic_manager.draw(self.screen)
            self.player.draw(self.screen)
            self.collision_manager.draw(self.screen)

            self.draw_dashboard_hud(self.screen, tracker_state)

            if self.state == GameState.PAUSED:
                self.draw_paused_screen(self.screen)

        elif self.state == GameState.HOME:
            self.draw_home_screen(self.screen)

        elif self.state == GameState.GAME_OVER:
            self.draw_game_over_screen(self.screen)

        pygame.display.flip()

    def run(self):
        # Main game loop with delta-time clamping
        last_time = time.time()
        try:
            while self.is_running:
                now = time.time()
                dt = min(now - last_time, 0.05)
                last_time = now

                self.handle_events()
                self.update(dt)
                self.render()

                self.clock.tick(config.FPS)
                self.current_fps = self.clock.get_fps()
        finally:
            self.cleanup()

    def cleanup(self):
        # Cleans up resources upon exit
        print("[Game] Cleaning up resources...")
        if hasattr(self, "hand_tracker") and self.hand_tracker:
            self.hand_tracker.stop()

        if hasattr(self, "high_score"):
            self.asset_manager.save_high_score(self.high_score)

        pygame.quit()
        print("[Game] Shutdown complete.")
