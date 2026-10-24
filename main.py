import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

def ensure_assets():
    """Checks if core assets exist. If not, auto-generates them."""
    road_bg_path = os.path.join(BASE_DIR, "assets", "backgrounds", "road_bg.png")
    player_car_path = os.path.join(BASE_DIR, "assets", "cars", "player_car.png")

    if not os.path.exists(road_bg_path) or not os.path.exists(player_car_path):
        print("[Launcher] Required assets missing. Generating procedural assets...")
        from tools import generate_assets
        generate_assets.main()

def main():
    print("Starting Hand Tracking Car Game...")
    ensure_assets()

    from src.game import Game
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
