import os
import math
import random
import pygame

os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

BG_DIR = os.path.join(ASSETS_DIR, "backgrounds")
CARS_DIR = os.path.join(ASSETS_DIR, "cars")
UI_DIR = os.path.join(ASSETS_DIR, "ui")

for d in [BG_DIR, CARS_DIR, UI_DIR]:
    os.makedirs(d, exist_ok=True)

def generate_road_bg(width=1000, height=700):
    surface = pygame.Surface((width, height))
    surface.fill((16, 20, 26))

    # Left Grass and Curb
    pygame.draw.rect(surface, (28, 54, 32), (0, 0, 50, height))
    random.seed(42)
    for _ in range(300):
        gx = random.randint(0, 48)
        gy = random.randint(0, height)
        c = random.randint(35, 65)
        surface.set_at((gx, gy), (20, c + 20, 25))

    for y in range(0, height, 20):
        color = (220, 220, 220) if (y // 20) % 2 == 0 else (180, 40, 40)
        pygame.draw.rect(surface, color, (44, y, 6, 20))

    # Road Asphalt
    road_rect = pygame.Rect(50, 0, 510, height)
    pygame.draw.rect(surface, (32, 35, 42), road_rect)

    for _ in range(3500):
        rx = random.randint(52, 558)
        ry = random.randint(0, height - 1)
        grain = random.randint(26, 46)
        surface.set_at((rx, ry), (grain, grain, grain + 4))

    # Outer yellow boundary lines
    pygame.draw.line(surface, (240, 190, 30), (52, 0), (52, height), 4)
    pygame.draw.line(surface, (240, 190, 30), (558, 0), (558, height), 4)

    # Lane Dividers
    dash_len = 35
    gap_len = 25
    total_dash = dash_len + gap_len
    for y in range(0, height, total_dash):
        pygame.draw.line(surface, (230, 235, 240), (220, y), (220, min(height, y + dash_len)), 3)
        pygame.draw.line(surface, (230, 235, 240), (390, y), (390, min(height, y + dash_len)), 3)

    # Curb stones on right
    for y in range(0, height, 20):
        color = (220, 220, 220) if (y // 20) % 2 == 0 else (180, 40, 40)
        pygame.draw.rect(surface, color, (560, y, 6, 20))

    # Hazard divider
    hazard_rect = pygame.Rect(566, 0, 34, height)
    pygame.draw.rect(surface, (20, 22, 28), hazard_rect)
    for y in range(-30, height + 30, 24):
        pygame.draw.line(surface, (210, 160, 20), (566, y), (600, y + 24), 5)

    # Dashboard Area
    dash_bg = pygame.Rect(600, 0, 400, height)
    pygame.draw.rect(surface, (14, 17, 24), dash_bg)
    for x in range(600, 1000, 40):
        pygame.draw.line(surface, (22, 28, 38), (x, 0), (x, height), 1)
    for y in range(0, height, 40):
        pygame.draw.line(surface, (22, 28, 38), (600, y), (1000, y), 1)

    pygame.draw.line(surface, (0, 180, 230), (600, 0), (600, height), 3)

    out_path = os.path.join(BG_DIR, "road_bg.png")
    pygame.image.save(surface, out_path)
    print(f"Generated: {out_path}")

def generate_home_bg(width=1000, height=700):
    surface = pygame.Surface((width, height))
    for y in range(height):
        factor = y / height
        r = int(10 + factor * 25)
        g = int(14 + factor * 18)
        b = int(32 + factor * 45)
        pygame.draw.line(surface, (r, g, b), (0, y), (width, y))

    horizon_y = 320
    for x in range(-200, width + 300, 70):
        pygame.draw.line(surface, (0, 140, 210, 70), (width // 2, horizon_y), (x, height), 2)
    for y in range(horizon_y + 10, height, 30):
        progress = (y - horizon_y) / (height - horizon_y)
        step_y = int(horizon_y + (progress ** 2) * (height - horizon_y))
        if step_y < height:
            pygame.draw.line(surface, (0, 100, 180), (0, step_y), (width, step_y), 1)

    for off in range(15):
        alpha = int(40 - off * 2.5)
        glow_s = pygame.Surface((width, 3), pygame.SRCALPHA)
        glow_s.fill((0, 200, 255, max(0, alpha)))
        surface.blit(glow_s, (0, horizon_y - 7 + off))

    random.seed(99)
    for _ in range(80):
        sx = random.randint(0, width)
        sy = random.randint(0, horizon_y - 10)
        c = random.randint(140, 230)
        surface.set_at((sx, sy), (c, c, 255))

    out_path = os.path.join(BG_DIR, "home_bg.png")
    pygame.image.save(surface, out_path)
    print(f"Generated: {out_path}")

def generate_game_over_bg(width=1000, height=700):
    surface = pygame.Surface((width, height))
    for y in range(height):
        factor = y / height
        r = int(30 + factor * 20)
        g = int(8 + factor * 6)
        b = int(12 + factor * 8)
        pygame.draw.line(surface, (r, g, b), (0, y), (width, y))

    vignette = pygame.Surface((width, height), pygame.SRCALPHA)
    center = (width // 2, height // 2)
    max_radius = math.sqrt(center[0] ** 2 + center[1] ** 2)
    for r_step in range(0, int(max_radius), 25):
        alpha = int((r_step / max_radius) * 160)
        pygame.draw.rect(vignette, (0, 0, 0, min(180, alpha)), (0, 0, width, height), 25)

    surface.blit(vignette, (0, 0))
    out_path = os.path.join(BG_DIR, "game_over_bg.png")
    pygame.image.save(surface, out_path)
    print(f"Generated: {out_path}")

# Generate car sprites
def draw_topdown_car(primary_color, secondary_color, accent_color, is_player=False):
    w, h = 64, 110
    surface = pygame.Surface((w, h), pygame.SRCALPHA)

    wheel_w, wheel_h = 10, 20
    wheels_pos = [(4, 16), (w - 14, 16), (4, 76), (w - 14, 76)]
    for wx, wy in wheels_pos:
        pygame.draw.rect(surface, (25, 25, 28), (wx, wy, wheel_w, wheel_h), border_radius=3)
        pygame.draw.line(surface, (180, 180, 190), (wx + 3, wy + 4), (wx + 3, wy + wheel_h - 5), 2)

    shadow = pygame.Surface((w - 16, h - 14), pygame.SRCALPHA)
    shadow.fill((0, 0, 0, 90))
    surface.blit(shadow, (8, 9))

    body_rect = pygame.Rect(10, 10, w - 20, h - 20)
    pygame.draw.rect(surface, primary_color, body_rect, border_radius=12)
    pygame.draw.rect(surface, secondary_color, body_rect, width=2, border_radius=12)

    hood_poly = [(16, 26), (w - 16, 26), (w - 18, 42), (18, 42)]
    pygame.draw.polygon(surface, secondary_color, hood_poly)
    pygame.draw.line(surface, accent_color, (w // 2, 12), (w // 2, 44), 3)

    front_windshield = [(16, 44), (w - 16, 44), (w - 14, 60), (14, 60)]
    pygame.draw.polygon(surface, (20, 32, 45), front_windshield)
    pygame.draw.line(surface, (150, 210, 255), (18, 46), (w - 22, 58), 2)

    roof_rect = pygame.Rect(14, 60, w - 28, 22)
    pygame.draw.rect(surface, primary_color, roof_rect)
    if is_player:
        pygame.draw.rect(surface, accent_color, (w // 2 - 4, 62, 8, 18), border_radius=2)
    else:
        pygame.draw.line(surface, accent_color, (w // 2, 60), (w // 2, 82), 3)

    rear_windshield = [(14, 82), (w - 14, 82), (16, 92), (w - 16, 92)]
    pygame.draw.polygon(surface, (20, 32, 45), rear_windshield)

    hl_color = (255, 255, 230) if not is_player else (180, 240, 255)
    pygame.draw.polygon(surface, hl_color, [(12, 11), (18, 11), (15, 17)])
    pygame.draw.polygon(surface, hl_color, [(w - 18, 11), (w - 12, 11), (w - 15, 17)])

    tl_color = (240, 30, 30)
    pygame.draw.rect(surface, tl_color, (12, h - 13, 8, 3), border_radius=1)
    pygame.draw.rect(surface, tl_color, (w - 20, h - 13, 8, 3), border_radius=1)

    spoiler_rect = pygame.Rect(8, h - 16, w - 16, 5)
    pygame.draw.rect(surface, secondary_color, spoiler_rect, border_radius=2)
    pygame.draw.rect(surface, accent_color, (w // 2 - 8, h - 16, 16, 5))

    pygame.draw.rect(surface, secondary_color, (7, 43, 4, 6), border_radius=2)
    pygame.draw.rect(surface, secondary_color, (w - 11, 43, 4, 6), border_radius=2)

    return surface

def generate_cars():
    player = draw_topdown_car((12, 130, 220), (8, 70, 130), (0, 240, 255), is_player=True)
    pygame.image.save(player, os.path.join(CARS_DIR, "player_car.png"))

    npc1 = draw_topdown_car((205, 35, 45), (120, 15, 25), (255, 240, 240))
    pygame.image.save(npc1, os.path.join(CARS_DIR, "npc_car_01.png"))

    npc2 = draw_topdown_car((235, 175, 20), (150, 105, 10), (40, 40, 40))
    pygame.image.save(npc2, os.path.join(CARS_DIR, "npc_car_02.png"))

    npc3 = draw_topdown_car((35, 185, 80), (18, 100, 45), (200, 255, 220))
    pygame.image.save(npc3, os.path.join(CARS_DIR, "npc_car_03.png"))

    npc4 = draw_topdown_car((150, 40, 210), (85, 20, 125), (255, 180, 255))
    pygame.image.save(npc4, os.path.join(CARS_DIR, "npc_car_04.png"))

# Generate UI elements
def draw_heart(filled=True, size=(40, 40)):
    w, h = size
    surface = pygame.Surface((w, h), pygame.SRCALPHA)
    pts = [
        (w * 0.5, h * 0.85),
        (w * 0.1, h * 0.45),
        (w * 0.15, h * 0.2),
        (w * 0.35, h * 0.15),
        (w * 0.5, h * 0.35),
        (w * 0.65, h * 0.15),
        (w * 0.85, h * 0.2),
        (w * 0.9, h * 0.45),
    ]

    if filled:
        pygame.draw.polygon(surface, (235, 35, 55), pts)
        pygame.draw.circle(surface, (255, 160, 175), (int(w * 0.32), int(h * 0.32)), int(w * 0.1))
        pygame.draw.polygon(surface, (140, 15, 25), pts, width=2)
    else:
        pygame.draw.polygon(surface, (45, 50, 60, 140), pts)
        pygame.draw.polygon(surface, (110, 115, 130), pts, width=2)

    return surface

def generate_ui():
    h_full = draw_heart(filled=True)
    pygame.image.save(h_full, os.path.join(UI_DIR, "heart_full.png"))
    h_empty = draw_heart(filled=False)
    pygame.image.save(h_empty, os.path.join(UI_DIR, "heart_empty.png"))

    button_labels = [
        ("start_button.png", "START", (0, 170, 230), (0, 70, 120)),
        ("exit_button.png", "EXIT", (210, 50, 60), (110, 20, 30)),
        ("restart_button.png", "RESTART", (0, 190, 140), (0, 90, 65)),
        ("resume_button.png", "RESUME", (0, 170, 230), (0, 70, 120)),
        ("home_button.png", "HOME", (150, 90, 220), (75, 40, 115))
    ]

    font = pygame.font.SysFont("arial", 22, bold=True)
    bw, bh = 220, 56

    for fname, text, color1, color2 in button_labels:
        bsurf = pygame.Surface((bw, bh), pygame.SRCALPHA)
        btn_rect = pygame.Rect(2, 2, bw - 4, bh - 4)

        for step in range(bh - 4):
            t = step / float(bh - 4)
            r = int(color1[0] * (1 - t * 0.4) + color2[0] * (t * 0.4))
            g = int(color1[1] * (1 - t * 0.4) + color2[1] * (t * 0.4))
            b = int(color1[2] * (1 - t * 0.4) + color2[2] * (t * 0.4))
            pygame.draw.line(bsurf, (r, g, b), (4, 2 + step), (bw - 5, 2 + step))

        pygame.draw.rect(bsurf, (255, 255, 255, 200), btn_rect, width=2, border_radius=14)
        pygame.draw.line(bsurf, (255, 255, 255, 140), (16, 4), (bw - 16, 4), 2)

        shadow = font.render(text, True, (10, 15, 20))
        tx = (bw - shadow.get_width()) // 2
        ty = (bh - shadow.get_height()) // 2
        bsurf.blit(shadow, (tx + 1, ty + 2))

        txt_img = font.render(text, True, (255, 255, 255))
        bsurf.blit(txt_img, (tx, ty))

        out_path = os.path.join(UI_DIR, fname)
        pygame.image.save(bsurf, out_path)

def main():
    print("Generating visual assets...")
    generate_road_bg()
    generate_home_bg()
    generate_game_over_bg()
    generate_cars()
    generate_ui()
    print("All assets generated successfully!")

if __name__ == "__main__":
    main()
