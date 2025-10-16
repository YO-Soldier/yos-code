import pygame

BASE_WIDTH, BASE_HEIGHT = 640, 480
SCREEN_WIDTH, SCREEN_HEIGHT = 320, 240
scale_x = SCREEN_WIDTH / BASE_WIDTH
scale_y = SCREEN_HEIGHT / BASE_HEIGHT

def scale_pos(x, y):
    return int(x*scale_x), int(y*scale_y)

def load_scaled_image(path, w=None, h=None):
    img = pygame.image.load(path).convert_alpha()
    if w and h:
        return pygame.transform.scale(img, (int(w*scale_x), int(h*scale_y)))
    else:
        return pygame.transform.scale(img, (int(img.get_width()*scale_x), int(img.get_height()*scale_y)))

import pygame, sys, math, random, os

# --- CONSTANTS ---
WIDTH, HEIGHT = 640, 480
FPS = 60
NUM_SECTORS = 37

# Ball behavior tuning
OUTER_HOLD_LAPS = 2.0       # 外周で保持する周回数
OUTER_RADIUS_START = 165.0  # 外周走行の半径（木枠の内側沿い）
PIN_RING_RADIUS = 140.0     # ディフレクターのリング半径
INNER_TARGET_RADIUS = 120.0 # 落下後の最終半径

pygame.init()

# --- AUTO RESOLUTION DETECT ---
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN | pygame.SCALED)
pygame.display.set_caption("Roulette")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 18)
bigfont = pygame.font.SysFont(None, 28)

# 仮想surface
virtual_surface = pygame.Surface((WIDTH, HEIGHT))

# --- SAFE STORAGE DIR DETECTION ---
def pick_storage_dir():
    candidates = []
    try:
        if getattr(sys, "frozen", False):
            candidates.append(os.path.dirname(sys.executable))
        else:
            candidates.append(os.path.dirname(os.path.abspath(__file__)))
    except Exception:
        pass
    try:
        candidates.append(os.getcwd())
    except Exception:
        pass
    try:
        candidates.append(os.path.join(os.path.expanduser("~"), ".pygame_roulette"))
    except Exception:
        pass
    for d in candidates:
        try:
            os.makedirs(d, exist_ok=True)
            test_path = os.path.join(d, ".write_test.tmp")
            with open(test_path, "w", encoding="utf-8") as f:
                f.write("ok")
            os.remove(test_path)
            return d
        except Exception:
            continue
    return os.getcwd()

STORAGE_DIR = pick_storage_dir()
MONEY_FILE = os.path.join(STORAGE_DIR, "money.txt")

def load_money():
    try:
        with open(MONEY_FILE, "r", encoding="utf-8") as f:
            s = f.read().strip()
            return int(s) if s else 2000
    except Exception:
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            legacy = os.path.join(script_dir, "money.txt")
            with open(legacy, "r", encoding="utf-8") as f:
                s = f.read().strip()
                return int(s) if s else 2000
        except Exception:
            return 2000

def save_money(val):
    try:
        os.makedirs(STORAGE_DIR, exist_ok=True)
        tmp = MONEY_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(str(int(val)))
        os.replace(tmp, MONEY_FILE)
    except Exception as e:
        try:
            print("Save error:", e)
        except Exception:
            pass

money = load_money()

# --- EUROPEAN ORDER ---
roulette_numbers = [
    0, 32, 15, 19, 4, 21, 2, 25, 17, 34,
    6, 27, 13, 36, 11, 30, 8, 23, 10, 5,
    24, 16, 33, 1, 20, 14, 31, 9, 22, 18,
    29, 7, 28, 12, 35, 3, 26
]

def get_color(num):
    if num == 0:
        return (0,200,0)  # green
    red_numbers = {1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}
    return (200,0,0) if num in red_numbers else (0,0,0)

# --- STATE ---
angle = 0.0
wheel_speed = 1.0
spinning = False
result = None
waiting_next = False

bets = {}
cursor_x, cursor_y = 100, 420
game_started = False

# --- BALL ---
ball_angle = 0.0
ball_speed = 0.0
ball_radius = 0.0
target_radius = 0.0
ball_active = False
ball_result_angle = None
ball_phase = "idle"
ball_travel_deg = 0.0

# --- CHIPS ---
chip_values = [1, 5, 10, 25, 50, 100, 250, 500]
chip_colors = {1:(255,255,255),5:(0,0,255),10:(220,0,0),25:(0,180,0),
               50:(255,215,0),100:(30,30,30),250:(255,140,0),500:(128,0,128)}
current_chip_index = 0
def current_chip(): return chip_values[current_chip_index]
def chip_color_for_amount(amount):
    cand = 1
    for v in chip_values:
        if amount >= v:
            cand = v
    return chip_colors.get(cand, (255,255,255))

# --- TABLE GEOM ---
SPIN_RECT = pygame.Rect(550, 440, 70, 30)
bet_rects = {}

def build_bet_table():
    global bet_rects
    bet_rects = {}
    x0, y0, w, h = 50, 330, 25, 25
    bet_rects[("num",0)] = pygame.Rect(x0 - w, y0, w, h*3)
    for row in range(12):
        for col in range(3):
            num = row*3 + (col+1)
            bet_rects[("num",num)] = pygame.Rect(x0 + row*w, y0 + (2-col)*h, w, h)
    bet_rects[("range","1-12")]  = pygame.Rect(x0 + 0*4*w, y0 + 3*h, 4*w, h)
    bet_rects[("range","13-24")] = pygame.Rect(x0 + 1*4*w, y0 + 3*h, 4*w, h)
    bet_rects[("range","25-36")] = pygame.Rect(x0 + 2*4*w, y0 + 3*h, 4*w, h)
    bet_rects[("range","1-18")]   = pygame.Rect(x0 + 0*2*w, y0 + 4*h, 2*w, h)
    bet_rects[("parity","even")]  = pygame.Rect(x0 + 1*2*w, y0 + 4*h, 2*w, h)
    bet_rects[("color","red")]    = pygame.Rect(x0 + 2*2*w, y0 + 4*h, 2*w, h)
    bet_rects[("color","black")]  = pygame.Rect(x0 + 3*2*w, y0 + 4*h, 2*w, h)
    bet_rects[("parity","odd")]   = pygame.Rect(x0 + 4*2*w, y0 + 4*h, 2*w, h)
    bet_rects[("range","19-36")]  = pygame.Rect(x0 + 5*2*w, y0 + 4*h, 2*w, h)
    for i in range(3):
        bet_rects[("col", i)] = pygame.Rect(x0 + 12*w, y0 + i*h, w, h)
    bet_rects[("spin","button")] = SPIN_RECT.copy()
build_bet_table()

# --- BET LOGIC ---
def save_money_safe():
    save_money(money)

def change_bet_at_key(key, chips_delta):
    global money
    if key not in bet_rects or key == ("spin","button"):
        return
    cv = current_chip()
    delta_amount = chips_delta * cv
    if delta_amount > 0:
        can = min(delta_amount, money)
        if can <= 0: return
        bets[key] = bets.get(key, 0) + can
        money -= can
        save_money_safe()
    elif delta_amount < 0:
        if key not in bets: return
        remove = min(-delta_amount, bets[key])
        bets[key] -= remove
        money += remove
        if bets[key] <= 0:
            bets.pop(key, None)
        save_money_safe()

def handle_click(pos, chips_delta):
    x, y = pos
    for key, rect in bet_rects.items():
        if rect.collidepoint(x, y):
            if key == ("spin","button") and chips_delta > 0:
                start_spin()
                return
            change_bet_at_key(key, chips_delta)
            return

def start_spin():
    global spinning, ball_active, result, waiting_next
    global ball_angle, ball_speed, ball_radius, target_radius
    global ball_result_angle, ball_phase, ball_travel_deg
    if spinning or not any(bets.values()):
        return
    ball_phase = "outer"
    ball_travel_deg = 0.0
    ball_speed = random.uniform(10.0, 14.0)
    ball_angle = random.uniform(0, 360)
    ball_radius = OUTER_RADIUS_START
    target_radius = OUTER_RADIUS_START
    ball_active = True
    spinning = True
    waiting_next = False
    result = None
    ball_result_angle = None

# --- DRAW HELPERS ---
def draw_bet_count(surface, rect, bet_key):
    if bet_key in bets and bets[bet_key] > 0:
        amount = bets[bet_key]
        color = chip_color_for_amount(amount)
        pygame.draw.circle(surface, color, rect.center, 10)
        txt_col = (255,255,255) if sum(color) < 300 else (0,0,0)
        txt = font.render(str(amount), True, txt_col)
        surface.blit(txt, txt.get_rect(center=rect.center))

def draw_roulette(surface, angle):
    center = (WIDTH//2, HEIGHT//2 - 80)
    radius = 140
    sector = 360 / NUM_SECTORS
    for i, num in enumerate(roulette_numbers):
        color = get_color(num)
        pts = [center]
        for a in range(int(sector)+1):
            rad = math.radians(sector*i + a + angle)
            x = center[0] + radius*math.cos(rad)
            y = center[1] + radius*math.sin(rad)
            pts.append((x,y))
        pygame.draw.polygon(surface, color, pts)
        t = math.radians(sector*(i+0.5) + angle)
        tx = center[0] + radius*0.7*math.cos(t)
        ty = center[1] + radius*0.7*math.sin(t)
        text = font.render(str(num), True, (255,255,255))
        surface.blit(text, text.get_rect(center=(tx,ty)))

def draw_deflectors(surface, cx, cy, radius, angle):
    sector = 360 / NUM_SECTORS
    length, thick = 12, 4
    for i in range(NUM_SECTORS):
        b = math.radians(sector*i + angle)
        dx = cx + radius*math.cos(b)
        dy = cy + radius*math.sin(b)
        t = b + math.pi/2
        ct, st = math.cos(t), math.sin(t)
        p1 = (dx - ct*length/2 - st*thick/2, dy - st*length/2 + ct*thick/2)
        p2 = (dx + ct*length/2 - st*thick/2, dy + st*length/2 + ct*thick/2)
        p3 = (dx + ct*length/2 + st*thick/2, dy + st*length/2 - ct*thick/2)
        p4 = (dx - ct*length/2 + st*thick/2, dy - st*length/2 - ct*thick/2)
        pygame.draw.polygon(surface, (200,200,200), [p1,p2,p3,p4])

def draw_ball(surface, cx, cy, radius, world_angle):
    rad = math.radians(world_angle)
    bx = cx + radius * math.cos(rad)
    by = cy + radius * math.sin(rad)
    pygame.draw.circle(surface, (255,255,255), (int(bx), int(by)), 8)
    return bx, by

def check_deflector_collision(cx, cy, radius, angle, ball_x, ball_y):
    sector = 360 / NUM_SECTORS
    for i in range(NUM_SECTORS):
        b = math.radians(sector*i + angle)
        dx = cx + radius*math.cos(b)
        dy = cy + radius*math.sin(b)
        if math.hypot(dx - ball_x, dy - ball_y) < 10:
            return True
    return False

def draw_bet_table(surface):
    for key, rect in bet_rects.items():
        if key == ("spin","button"):
            pygame.draw.rect(surface,(0,120,220),rect,border_radius=10)
            pygame.draw.rect(surface,(255,255,255),rect,3,border_radius=10)
            spin_txt = bigfont.render("SPIN", True, (255,255,255))
            surface.blit(spin_txt, spin_txt.get_rect(center=rect.center))
            continue
        if key[0] == "num":
            num = key[1]
            color = get_color(num)
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, (255,255,255), rect, 2)
            txt = font.render(str(num), True, (255,255,255))
            surface.blit(txt, txt.get_rect(center=rect.center))
            draw_bet_count(surface, rect, key)
        elif key[0] in ("range","parity","color"):
            pygame.draw.rect(surface, (50,50,50), rect)
            pygame.draw.rect(surface, (255,255,255), rect, 2)
            label = str(key[1]).upper()
            txt = font.render(label, True, (255,255,255))
            surface.blit(txt, txt.get_rect(center=rect.center))
            draw_bet_count(surface, rect, key)
        elif key[0] == "col":
            pygame.draw.rect(surface, (50,50,50), rect)
            pygame.draw.rect(surface, (255,255,255), rect, 2)
            txt = font.render("row", True, (255,255,255))
            surface.blit(txt, txt.get_rect(center=rect.center))
            draw_bet_count(surface, rect, key)

# --- PAYOUT ---
def payout(num):
    win = 0
    for (bet_type,val),amount in bets.items():
        if amount <= 0: 
            continue
        if bet_type == "num" and val == num:
            win += amount * 36
        elif bet_type == "range":
            if val == "1-12"  and 1<=num<=12:  win += amount * 3
            if val == "13-24" and 13<=num<=24: win += amount * 3
            if val == "25-36" and 25<=num<=36: win += amount * 3
            if val == "1-18"  and 1<=num<=18:  win += amount * 2
            if val == "19-36" and 19<=num<=36: win += amount * 2
        elif bet_type == "color":
            if val == "red"   and get_color(num)==(200,0,0): win += amount * 2
            if val == "black" and get_color(num)==(0,0,0): win += amount * 2
        elif bet_type == "parity":
            if val == "even" and num!=0 and num%2==0: win += amount * 2
            if val == "odd"  and num%2==1:           win += amount * 2
        elif bet_type == "col":
            i = val
            col_index = 2 - i
            if num != 0 and ((num-1) % 3) == col_index:
                win += amount * 3
    return win

def get_result_from_ball(wheel_angle_deg, ball_world_angle_deg):
    sector = 360 / NUM_SECTORS
    rel = (ball_world_angle_deg - wheel_angle_deg) % 360
    idx = int(rel // sector)
    return roulette_numbers[idx]

def main():
    global game_started, waiting_next, cursor_x, cursor_y, angle
    global current_chip_index
    global spinning, ball_active, result, ball_result_angle, ball_phase, ball_travel_deg
    global ball_angle, ball_speed, ball_radius, target_radius
    global money, bets

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_money(money)
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if not game_started:
                    if event.key == pygame.K_RETURN:
                        game_started = True
                elif waiting_next:
                    if event.key == pygame.K_LCTRL:
                        waiting_next = False
                        result = None
                        ball_result_angle = None
                    elif event.key == pygame.K_LALT:
                        save_money(money)
                        sys.exit()
                else:
                    if event.key == pygame.K_PAGEUP:
                        current_chip_index = (current_chip_index - 1) % len(chip_values)
                    elif event.key == pygame.K_PAGEDOWN:
                        current_chip_index = (current_chip_index + 1) % len(chip_values)
                    elif event.key == pygame.K_SPACE:
                        save_money(money)
                        sys.exit()
                    elif event.key == pygame.K_RETURN:
                        handle_click((cursor_x, cursor_y), +1)
                    elif event.key == pygame.K_SPACE:
                        handle_click((cursor_x, cursor_y), -1)

        keys = pygame.key.get_pressed()
        if game_started and not waiting_next:
            if keys[pygame.K_LEFT]:  cursor_x -= 3
            if keys[pygame.K_RIGHT]: cursor_x += 3
            if keys[pygame.K_UP]:    cursor_y -= 3
            if keys[pygame.K_DOWN]:  cursor_y += 3
        cursor_x = max(0, min(WIDTH, cursor_x))
        cursor_y = max(0, min(HEIGHT, cursor_y))

        angle = (angle + wheel_speed) % 360

        center = (WIDTH//2, HEIGHT//2 - 80)
        if ball_active:
            ball_angle = (ball_angle - ball_speed) % 360
            ball_travel_deg += ball_speed

            if ball_phase == "outer":
                ball_speed *= 0.998
                target_radius = OUTER_RADIUS_START + math.sin(pygame.time.get_ticks()*0.01)*0.5
                ball_radius += (target_radius - ball_radius) * 0.25

                if ball_travel_deg >= OUTER_HOLD_LAPS * 360.0:
                    ball_phase = "drop"
                    target_radius = INNER_TARGET_RADIUS

            elif ball_phase == "drop":
                ball_speed *= 0.990
                ball_radius += (target_radius - ball_radius) * 0.06

                world_angle = (angle + ball_angle) % 360
                bx = center[0] + ball_radius * math.cos(math.radians(world_angle))
                by = center[1] + ball_radius * math.sin(math.radians(world_angle))

                if ball_radius <= PIN_RING_RADIUS + 6:
                    if check_deflector_collision(center[0], center[1], PIN_RING_RADIUS, angle, bx, by):
                        ball_angle = (ball_angle + random.uniform(-12, 12)) % 360
                        ball_speed *= 0.85

                if ball_speed < 0.12 and abs(ball_radius - target_radius) < 2:
                    ball_active = False
                    spinning = False
                    world_angle = (angle + ball_angle) % 360
                    result = get_result_from_ball(angle, world_angle)
                    money += payout(result)
                    save_money(money)
                    bets.clear()
                    waiting_next = True
                    ball_result_angle = world_angle

        else:
            if result is not None and ball_result_angle is not None:
                ball_result_angle = (ball_result_angle + wheel_speed) % 360

        # --- DRAW ---
        virtual_surface.fill((0,120,0))
        center = (WIDTH//2, HEIGHT//2 - 80)

        WOOD_BASE = (139, 69, 19)
        outer_r = 170
        inner_r = 140
        steps = 6
        for i in range(steps):
            t = i / max(steps-1, 1)
            col = (int(WOOD_BASE[0]*(0.9+0.1*t)),
                int(WOOD_BASE[1]*(0.9+0.1*t)),
                int(WOOD_BASE[2]*(0.9+0.1*t)))
            r = int(outer_r - (outer_r - inner_r) * (i/steps))
            pygame.draw.circle(virtual_surface, col, center, r)
        pygame.draw.circle(virtual_surface, (0,120,0), center, inner_r)

        draw_roulette(virtual_surface, angle)
        draw_deflectors(virtual_surface, center[0], center[1], PIN_RING_RADIUS, angle)

        if ball_active:
            world_angle = (angle + ball_angle) % 360
            draw_ball(virtual_surface, center[0], center[1],
                    ball_radius if ball_phase != "idle" else INNER_TARGET_RADIUS,
                    world_angle)
        elif result is not None and ball_result_angle is not None:
            draw_ball(virtual_surface, center[0], center[1], INNER_TARGET_RADIUS, ball_result_angle)

        draw_bet_table(virtual_surface)
        pygame.draw.circle(virtual_surface, (255,255,0), (cursor_x, cursor_y), 5)

        virtual_surface.blit(bigfont.render(f"MONEY: {money}$", True, (255,255,255)), (10, 10))
        virtual_surface.blit(bigfont.render(f"CHIP: {current_chip()}  [ / ]", True, (255,255,255)), (10, 40))

        if not game_started:
            msg = bigfont.render("PRESS RETURN TO RUNGAME", True, (255,255,0))
            virtual_surface.blit(msg, msg.get_rect(center=(WIDTH//2, HEIGHT//2)))
        if waiting_next and result is not None:
            c = 'GREEN' if result==0 else ('RED' if get_color(result)==(200,0,0) else 'BLACK')
            res_txt = bigfont.render(f"RESULT: {result} ({c})", True, (255,255,255))
            virtual_surface.blit(res_txt, (WIDTH//2-110, 60))
            virtual_surface.blit(bigfont.render("PRESS RETURN FOR NEXT OR SPACE TO END", True, (255,255,0)),
                        (WIDTH//2-170, HEIGHT-40))

        # --- SCALE & BLIT ---
        scaled = pygame.transform.smoothscale(virtual_surface, (WIDTH, HEIGHT))
        screen.blit(scaled, (0,0))

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
