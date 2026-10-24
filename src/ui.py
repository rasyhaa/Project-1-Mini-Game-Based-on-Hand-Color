from typing import Optional, Tuple, Callable
import pygame
import config
from src.asset_manager import AssetManager

class Button:
    """Interactive button with hover animation and click sound."""

    def __init__(self, x: int, y: int, image: pygame.Surface, callback: Optional[Callable] = None):
        self.normal_image = image
        self.rect = self.normal_image.get_rect(center=(x, y))
        self.callback = callback
        self.is_hovered = False

        # Pre-render hover effect (brightened with subtle cyan glow)
        w, h = self.normal_image.get_size()
        self.hover_image = pygame.Surface((w, h), pygame.SRCALPHA)
        self.hover_image.blit(self.normal_image, (0, 0))
        # Cyan outline
        pygame.draw.rect(self.hover_image, config.COLOR_CYAN, (0, 0, w, h), width=3, border_radius=14)

    def update(self, mouse_pos: Tuple[int, int]):
        """Updates hover status."""
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def handle_event(self, event: pygame.event.Event, asset_manager: AssetManager) -> bool:
        """Processes mouse clicks and triggers callback."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if getattr(config, "ENABLE_SOUND", False):
                    asset_manager.play_sound("audio/button_click.wav", volume=0.7)
                if self.callback:
                    self.callback()
                return True
        return False

    def draw(self, surface: pygame.Surface):
        """Draws button in current state."""
        img = self.hover_image if self.is_hovered else self.normal_image
        surface.blit(img, self.rect.topleft)


class UIRenderer:
    """Manages dashboard rendering, screens, and HUD layouts."""

    def __init__(self, asset_manager: AssetManager):
        self.asset_manager = asset_manager

        # Road animation scroll offset
        self.road_scroll_offset = 0.0

    def update_road_scroll(self, dt: float):
        """Updates the scrolling illusion of road lane dividers."""
        self.road_scroll_offset = (self.road_scroll_offset + config.SCROLL_SPEED * dt) % 60.0

    def draw_road_dividers(self, surface: pygame.Surface):
        """Draws animated dashed white lane divider stripes."""
        dash_len = 35
        gap_len = 25
        cycle = dash_len + gap_len

        for base_y in range(-cycle, config.SCREEN_HEIGHT + cycle, cycle):
            y = base_y + int(self.road_scroll_offset)
            # Lane divider 1 at x = 220
            pygame.draw.line(surface, config.COLOR_WHITE, (220, y), (220, y + dash_len), 4)
            # Lane divider 2 at x = 390
            pygame.draw.line(surface, config.COLOR_WHITE, (390, y), (390, y + dash_len), 4)

    def draw_dashboard_hud(self, surface: pygame.Surface, lives: int, tracker_state: dict, *args, **kwargs):
        """
        Renders the right-side dashboard (x = 600 to 1000):
        Contains ONLY:
        1. Lives (Heart icons)
        2. Webcam preview feed
        """
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
            h_img = heart_full if i < lives else heart_empty
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

    def draw_home_screen(self, surface: pygame.Surface, buttons: list, high_score: int):
        """Renders the Home Screen menu."""
        home_bg = self.asset_manager.load_image("backgrounds/home_bg.png", (config.SCREEN_WIDTH, config.SCREEN_HEIGHT), use_alpha=False)
        surface.blit(home_bg, (0, 0))

        font_title = self.asset_manager.get_font("title")
        font_header = self.asset_manager.get_font("header")
        font_small = self.asset_manager.get_font("small")

        # Title shadow & glow
        title_str = "Hand Tracking Car Game"
        t_shadow = font_title.render(title_str, True, (0, 30, 60))
        t_glow = font_title.render(title_str, True, config.COLOR_CYAN)
        surface.blit(t_shadow, (config.SCREEN_WIDTH // 2 - t_shadow.get_width() // 2 + 2, 72))
        surface.blit(t_glow, (config.SCREEN_WIDTH // 2 - t_glow.get_width() // 2, 70))

        # High score banner
        hs_str = f"HIGH SCORE: {high_score:06d}"
        hs_surf = font_header.render(hs_str, True, config.COLOR_WHITE)
        surface.blit(hs_surf, (config.SCREEN_WIDTH // 2 - hs_surf.get_width() // 2, 140))

        # Showcase player car in center
        player_car = self.asset_manager.load_image("cars/player_car.png", (84, 144))
        surface.blit(player_car, (config.SCREEN_WIDTH // 2 - 42, 215))

        # Draw buttons
        for btn in buttons:
            btn.draw(surface)

    def draw_paused_screen(self, surface: pygame.Surface, buttons: list):
        """Draws pause overlay on top of current gameplay."""
        dim_surf = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
        dim_surf.fill((10, 15, 22, 200))
        surface.blit(dim_surf, (0, 0))

        font_title = self.asset_manager.get_font("title")
        p_txt = font_title.render("GAME PAUSED", True, config.COLOR_CYAN)
        surface.blit(p_txt, p_txt.get_rect(center=(config.SCREEN_WIDTH // 2, 220)))

        for btn in buttons:
            btn.draw(surface)

    def draw_game_over_screen(self, surface: pygame.Surface, buttons: list, final_score: int, high_score: int):
        """Renders Game Over screen with score summaries."""
        bg = self.asset_manager.load_image("backgrounds/game_over_bg.png", (config.SCREEN_WIDTH, config.SCREEN_HEIGHT), use_alpha=False)
        surface.blit(bg, (0, 0))

        font_title = self.asset_manager.get_font("title")
        font_header = self.asset_manager.get_font("header")
        font_body = self.asset_manager.get_font("body")

        # Game Over Header
        go_txt = font_title.render("GAME OVER", True, config.COLOR_RED)
        surface.blit(go_txt, go_txt.get_rect(center=(config.SCREEN_WIDTH // 2, 160)))

        # Score Box
        box_rect = pygame.Rect(config.SCREEN_WIDTH // 2 - 200, 240, 400, 160)
        box_surf = pygame.Surface((400, 160), pygame.SRCALPHA)
        box_surf.fill((20, 24, 34, 220))
        pygame.draw.rect(box_surf, config.COLOR_RED, (0, 0, 400, 160), width=2, border_radius=12)
        surface.blit(box_surf, box_rect.topleft)

        score_txt = font_header.render(f"FINAL SCORE: {final_score:06d}", True, config.COLOR_YELLOW)
        high_txt = font_body.render(f"HIGH SCORE:  {high_score:06d}", True, config.COLOR_WHITE)

        is_new_best = final_score >= high_score and final_score > 0
        tag_str = "★ NEW HIGH SCORE! ★" if is_new_best else "BETTER LUCK NEXT RUN!"
        tag_color = config.COLOR_GREEN if is_new_best else config.COLOR_GRAY_LIGHT
        tag_surf = font_body.render(tag_str, True, tag_color)

        surface.blit(score_txt, score_txt.get_rect(center=(config.SCREEN_WIDTH // 2, 280)))
        surface.blit(high_txt, high_txt.get_rect(center=(config.SCREEN_WIDTH // 2, 325)))
        surface.blit(tag_surf, tag_surf.get_rect(center=(config.SCREEN_WIDTH // 2, 365)))

        for btn in buttons:
            btn.draw(surface)
