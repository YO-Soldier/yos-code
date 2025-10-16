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

import os, pygame, random, sys

# 仮想解像度
WIDTH, HEIGHT = 640, 480

# 初期化
pygame.init()
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
PLAYER_IMG_PATH = BASE_PATH + "/Images/player.png"
ENEMY_IMG_PATH  = BASE_PATH + "/Images/Thorn.png"
BG_IMG_PATH     = BASE_PATH + "/Images/bg.png"
COIN_IMG_PATH   = BASE_PATH + "/Images/coin.png"

# フルスクリーン (SCALED)
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN | pygame.SCALED)
pygame.display.set_caption("横スクロール障害物回避ゲーム")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 40)

# 色
WHITE = (255,255,255)
RED   = (255,0,0)

# プレイヤー設定
player_size = 40
player_x = 100
player_y = HEIGHT // 2
player_speed = 5

# 画像読み込み（仮想解像度基準）
bg_img     = pygame.image.load(BG_IMG_PATH).convert()
bg_img     = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))

enemy_img  = pygame.image.load(ENEMY_IMG_PATH).convert_alpha()
enemy_img  = pygame.transform.scale(enemy_img, (50, 100))

player_img = pygame.image.load(PLAYER_IMG_PATH).convert_alpha()
player_img = pygame.transform.scale(player_img, (50, 50))

coin_img   = pygame.image.load(COIN_IMG_PATH).convert_alpha()
coin_img   = pygame.transform.scale(coin_img, (35, 35))

# 障害物 & コイン
obstacle_list, coin_list = [], []
spawn_timer, coin_timer = 0, 0
spawn_interval, coin_interval = 1500, 2000

# スコア
score = 0
start_ticks = pygame.time.get_ticks()
game_over = False

def draw_text(surface, text, x, y, color=(0,0,0)):
    img = font.render(text, True, color)
    surface.blit(img, (x, y))

def main():
    global game_over, player_y, spawn_timer, coin_timer
    global obstacle_list, coin_list, score, start_ticks

    running = True
    while running:
        dt = clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()

        if not game_over:
            # プレイヤー操作
            if keys[pygame.K_UP]:   player_y -= player_speed
            if keys[pygame.K_DOWN]: player_y += player_speed
            if keys[pygame.K_SPACE]:
                running = False

            # 画面外制限
            player_y = max(0, min(HEIGHT - player_img.get_height(), player_y))

            # 障害物生成
            spawn_timer += dt
            if spawn_timer > spawn_interval:
                spawn_timer = 0
                obs_y = random.randint(0, HEIGHT - enemy_img.get_height())
                obstacle_list.append([WIDTH, obs_y])

            # コイン生成
            coin_timer += dt
            if coin_timer > coin_interval:
                coin_timer = 0
                coin_y = random.randint(0, HEIGHT - coin_img.get_height())
                coin_list.append([WIDTH, coin_y])

            # 移動
            for obs in obstacle_list: obs[0] -= 5
            for coin in coin_list:    coin[0] -= 5

        # プレイヤー矩形
        player_rect = pygame.Rect(player_x, player_y, player_size, player_size)

        # 障害物衝突
        for obs in obstacle_list:
            if player_rect.colliderect(pygame.Rect(obs[0], obs[1], enemy_img.get_width(), enemy_img.get_height())):
                game_over = True

        # コイン取得
        new_coin_list = []
        for c in coin_list:
            coin_rect = pygame.Rect(c[0], c[1], coin_img.get_width(), coin_img.get_height())
            if player_rect.colliderect(coin_rect):
                score += 10
            else:
                new_coin_list.append(c)
        coin_list = new_coin_list

        # スコア
        time_score = (pygame.time.get_ticks() - start_ticks) // 1000
        total_score = score + time_score

        # --- 描画 ---
        screen.blit(bg_img, (0,0))
        for obs in obstacle_list: screen.blit(enemy_img, obs)
        for coin in coin_list:    screen.blit(coin_img, coin)
        screen.blit(player_img, (player_x, player_y))
        draw_text(screen, f"Score: {total_score}", 10, 10)

        if game_over:
            draw_text(screen, "GAME OVER", WIDTH//2-100, HEIGHT//2-20, RED)
            draw_text(screen, "Press Y / LShift to Restart, X / Space to Exit", WIDTH//2-130, HEIGHT//2+30, (0,0,0))
            if keys[pygame.K_LSHIFT]:
                obstacle_list, coin_list = [], []
                player_y = HEIGHT // 2
                score = 0
                start_ticks = pygame.time.get_ticks()
                game_over = False

            if keys[pygame.K_SPACE]:
                running = False

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
