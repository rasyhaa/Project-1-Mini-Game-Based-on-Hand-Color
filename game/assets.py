import os
import json
import pygame
from game import config

class AssetManager:
    def __init__(self):
        self.images = {}
        self.fonts = {}
        self._load_fonts()
        self.load_all_assets()

    def _load_fonts(self):
        if not pygame.font.get_init():
            pygame.font.init()
        try:
            self.fonts["title"] = pygame.font.SysFont("impact", 44)
            self.fonts["header"] = pygame.font.SysFont("arial", 28, bold=True)
            self.fonts["body"] = pygame.font.SysFont("arial", 20, bold=True)
            self.fonts["small"] = pygame.font.SysFont("arial", 15)
            self.fonts["mono"] = pygame.font.SysFont("monospace", 14, bold=True)
        except Exception:
            self.fonts["title"] = pygame.font.Font(None, 52)
            self.fonts["header"] = pygame.font.Font(None, 34)
            self.fonts["body"] = pygame.font.Font(None, 24)
            self.fonts["small"] = pygame.font.Font(None, 18)
            self.fonts["mono"] = pygame.font.Font(None, 18)

    def load_image(self, rel_path, size=None, use_alpha=True):
        full_path = os.path.join(config.ASSETS_DIR, rel_path)
        cache_key = (rel_path, size)

        if cache_key in self.images:
            return self.images[cache_key]

        if os.path.exists(full_path):
            try:
                surf = pygame.image.load(full_path)
                if pygame.display.get_surface() is not None:
                    surf = surf.convert_alpha() if use_alpha else surf.convert()
                if size is not None:
                    surf = pygame.transform.smoothscale(surf, size)
                self.images[cache_key] = surf
                return surf
            except Exception as e:
                print(f"[AssetManager] Failed to load image {full_path}: {e}")

        # Fallback surface
        w, h = size if size else (64, 64)
        fallback = pygame.Surface((w, h), pygame.SRCALPHA if use_alpha else 0)
        fallback.fill((200, 50, 50, 180) if use_alpha else (200, 50, 50))
        pygame.draw.rect(fallback, (255, 255, 255), (0, 0, w, h), 2)
        self.images[cache_key] = fallback
        return fallback

    def load_all_assets(self):
        # Backgrounds
        self.load_image("backgrounds/road_bg.png", (config.SCREEN_WIDTH, config.SCREEN_HEIGHT), use_alpha=False)
        self.load_image("backgrounds/home_bg.png", (config.SCREEN_WIDTH, config.SCREEN_HEIGHT), use_alpha=False)
        self.load_image("backgrounds/game_over_bg.png", (config.SCREEN_WIDTH, config.SCREEN_HEIGHT), use_alpha=False)

        # Cars
        self.load_image("cars/player_car.png", (config.PLAYER_WIDTH, config.PLAYER_HEIGHT))
        self.load_image("cars/npc_car_01.png", (config.NPC_WIDTH, config.NPC_HEIGHT))
        self.load_image("cars/npc_car_02.png", (config.NPC_WIDTH, config.NPC_HEIGHT))
        self.load_image("cars/npc_car_03.png", (config.NPC_WIDTH, config.NPC_HEIGHT))
        self.load_image("cars/npc_car_04.png", (config.NPC_WIDTH, config.NPC_HEIGHT))

        # UI elements
        self.load_image("ui/heart_full.png", (36, 36))
        self.load_image("ui/heart_empty.png", (36, 36))
        self.load_image("ui/start_button.png", (220, 56))
        self.load_image("ui/exit_button.png", (220, 56))
        self.load_image("ui/restart_button.png", (220, 56))
        self.load_image("ui/resume_button.png", (220, 56))
        self.load_image("ui/home_button.png", (220, 56))

    def get_font(self, font_name="body"):
        return self.fonts.get(font_name, self.fonts["body"])

    # High score local persistence
    @staticmethod
    def load_high_score():
        if os.path.exists(config.HIGHSCORE_PATH):
            try:
                with open(config.HIGHSCORE_PATH, "r") as f:
                    data = json.load(f)
                    return int(data.get("high_score", 0))
            except Exception as e:
                print(f"[AssetManager] Error reading high score: {e}")
        return 0

    @staticmethod
    def save_high_score(new_score):
        current = AssetManager.load_high_score()
        if new_score > current:
            try:
                with open(config.HIGHSCORE_PATH, "w") as f:
                    json.dump({"high_score": new_score}, f, indent=4)
                return True
            except Exception as e:
                print(f"[AssetManager] Error saving high score: {e}")
        return False
