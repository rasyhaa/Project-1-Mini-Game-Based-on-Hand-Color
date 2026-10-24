import os
import json
import pygame
import config

class AssetManager:
    """Singleton-style asset manager for caching surfaces, fonts, and sound effects."""

    def __init__(self):
        self.images = {}
        self.sounds = {}
        self.fonts = {}
        self.audio_available = False
        self._init_audio()
        self._load_fonts()
        self.load_all_assets()

    def _init_audio(self):
        """Initializes Pygame mixer safely with graceful fallback, if enabled."""
        if not getattr(config, "ENABLE_SOUND", True):
            self.audio_available = False
            return

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            self.audio_available = True
        except Exception as e:
            print(f"[AssetManager] Audio device unavailable: {e}. Running with audio muted.")
            self.audio_available = False

    def _load_fonts(self):
        """Pre-loads common font sizes."""
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
        """
        Loads an image from assets directory with caching.
        Falls back to a colored placeholder if file is not found.
        """
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

        # Fallback procedural surface
        print(f"[AssetManager] Generating fallback surface for {rel_path}")
        w, h = size if size else (64, 64)
        fallback = pygame.Surface((w, h), pygame.SRCALPHA if use_alpha else 0)
        fallback.fill((200, 50, 50, 180) if use_alpha else (200, 50, 50))
        pygame.draw.rect(fallback, (255, 255, 255), (0, 0, w, h), 2)
        self.images[cache_key] = fallback
        return fallback

    def load_sound(self, rel_path):
        """Loads a sound effect if audio is available."""
        if not self.audio_available:
            return None

        full_path = os.path.join(config.ASSETS_DIR, rel_path)
        if rel_path in self.sounds:
            return self.sounds[rel_path]

        if os.path.exists(full_path):
            try:
                sound = pygame.mixer.Sound(full_path)
                self.sounds[rel_path] = sound
                return sound
            except Exception as e:
                print(f"[AssetManager] Failed to load sound {full_path}: {e}")

        return None

    def play_sound(self, key, volume=1.0):
        """Plays a loaded sound effect safely."""
        if not self.audio_available:
            return
        snd = self.sounds.get(key)
        if snd:
            snd.set_volume(volume)
            snd.play()

    def load_all_assets(self):
        """Pre-loads all core game assets."""
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

        # UI
        self.load_image("ui/heart_full.png", (36, 36))
        self.load_image("ui/heart_empty.png", (36, 36))
        self.load_image("ui/start_button.png", (220, 56))
        self.load_image("ui/exit_button.png", (220, 56))
        self.load_image("ui/restart_button.png", (220, 56))
        self.load_image("ui/resume_button.png", (220, 56))
        self.load_image("ui/home_button.png", (220, 56))

    def get_font(self, font_name="body"):
        """Retrieves cached font by identifier."""
        return self.fonts.get(font_name, self.fonts["body"])

    # High score local persistence
    @staticmethod
    def load_high_score():
        """Reads high score from local JSON file."""
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
        """Saves new high score to local JSON file if greater than current."""
        current = AssetManager.load_high_score()
        if new_score > current:
            try:
                with open(config.HIGHSCORE_PATH, "w") as f:
                    json.dump({"high_score": new_score}, f, indent=4)
                return True
            except Exception as e:
                print(f"[AssetManager] Error saving high score: {e}")
        return False
