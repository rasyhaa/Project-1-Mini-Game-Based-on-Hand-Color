import os
import numpy as np

# Audio setting (sound disabled)
ENABLE_SOUND = False

# Directories and paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

BG_DIR = os.path.join(ASSETS_DIR, "backgrounds")
CARS_DIR = os.path.join(ASSETS_DIR, "cars")
UI_DIR = os.path.join(ASSETS_DIR, "ui")
HIGHSCORE_PATH = os.path.join(ASSETS_DIR, "highscore.json")

# Display and window settings
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
FPS = 60
WINDOW_TITLE = "Hand Tracking Car Game"

# Road and lane geometry
# Road asphalt covers x = 50 to 560 (width = 510)
# 3 Fixed Lanes, each 170 px wide:
# Lane 0 (Left):   [50,  220] -> Center = 135
# Lane 1 (Center): [220, 390] -> Center = 305
# Lane 2 (Right):  [390, 560] -> Center = 475
ROAD_LEFT = 50
ROAD_RIGHT = 560
ROAD_WIDTH = ROAD_RIGHT - ROAD_LEFT
LANE_WIDTH = ROAD_WIDTH // 3
LANE_CENTERS = [
    ROAD_LEFT + LANE_WIDTH // 2,                     # Lane 0: 135
    ROAD_LEFT + LANE_WIDTH + LANE_WIDTH // 2,         # Lane 1: 305
    ROAD_LEFT + (2 * LANE_WIDTH) + LANE_WIDTH // 2   # Lane 2: 475
]
LANE_COUNT = 3

# Dashboard HUD on right side (x = 600 to 1000)
DASHBOARD_X = 600
DASHBOARD_WIDTH = SCREEN_WIDTH - DASHBOARD_X

# Player car settings
PLAYER_START_LANE = 1  # Center lane
PLAYER_Y = 560
PLAYER_WIDTH = 64
PLAYER_HEIGHT = 110
PLAYER_LIVES = 3
LANE_CHANGE_LERP_SPEED = 22.0   # Smooth interpolation towards target lane center
INVULNERABILITY_DURATION = 1.3  # Seconds of invulnerability and blinking after crash

# Traffic and NPC settings
SCROLL_SPEED = 320.0            # Base road scrolling speed (pixels/sec)
BASE_NPC_SPEED = 260.0          # Base NPC downward velocity relative to road
MAX_NPC_SPEED = 520.0           # Maximum NPC downward velocity
BASE_SPAWN_INTERVAL = 1.25      # Initial spawn interval in seconds
MIN_SPAWN_INTERVAL = 0.55       # Minimum spawn interval under peak difficulty
MIN_NPC_VERTICAL_GAP = 230      # Minimum vertical distance between consecutive cars in same lane
MAX_ACTIVE_NPCS = 6             # Upper bound of concurrent NPCs

# NPC Car Dimensions
NPC_WIDTH = 64
NPC_HEIGHT = 110

# Scoring and difficulty
SCORE_PER_SECOND = 10
SCORE_PER_PASS = 50
DIFFICULTY_RAMP_INTERVAL = 10.0 # Increase difficulty every 10 seconds

# HSV blue color detection and webcam motion tracking
WEBCAM_INDEX = 0
WEBCAM_FRAME_WIDTH = 320
WEBCAM_FRAME_HEIGHT = 240
WEBCAM_FPS = 30

# HSV Range for Blue Color Detection
# H: 0-180, S: 0-255, V: 0-255
LOWER_BLUE = np.array([90, 80, 50], dtype=np.uint8)
UPPER_BLUE = np.array([135, 255, 255], dtype=np.uint8)

# Contour filtering
MIN_CONTOUR_AREA = 1000         # Ignore contours smaller than this area (px^2)

# Dynamic Hand Motion / Swipe Detection
SWIPE_THRESHOLD_PX = 32         # Horizontal movement distance (px) to trigger lane shift
GESTURE_COOLDOWN = 0.32         # Cooldown in seconds between consecutive lane shifts
BASELINE_DRIFT_FACTOR = 0.06    # Leaky baseline adjustment rate for gentle drift

# Colors (RGB and RGBA)
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_GRAY_DARK = (20, 24, 32)
COLOR_GRAY_LIGHT = (180, 185, 195)
COLOR_CYAN = (0, 220, 255)
COLOR_BLUE_HUD = (10, 140, 230)
COLOR_GREEN = (40, 215, 90)
COLOR_RED = (235, 45, 55)
COLOR_YELLOW = (250, 195, 30)
COLOR_ORANGE = (255, 130, 20)
