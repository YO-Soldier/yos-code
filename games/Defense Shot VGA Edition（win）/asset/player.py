import pygame
import sys
import random
import os

import pygame
import sys
import random
import os

# --- 定数 ---
WIDTH = 640
HEIGHT = 480
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
FPS = 60

# 弾の発射間隔 (ms)
SHOT_DELAY_DEFAULT = 250   # 4発/秒
SHOT_DELAY_RIFLE   = 125   # 8発/秒
SHOT_DELAY_MG      = 67    # 15発/秒

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
ENEMY_IMG_PATH   = BASE_PATH + "/Images/enemy.png"
BOSS_IMG_PATH    = BASE_PATH + "/Images/boss.png"
PLAYER_IMG_PATH  = BASE_PATH + "/Images/player.png"
ARMY_IMG_PATH    = BASE_PATH + "/Images/army.png"
MG_IMG_PATH      = BASE_PATH + "/Images/mg.png"
RIFLE_IMG_PATH   = BASE_PATH + "/Images/rifle.png"
SHIELD_IMG_PATH  = BASE_PATH + "/Images/shield.png"
BACKGROUND_IMG_PATH = BASE_PATH + "/Images/bg.png"

# --- グローバル（スプライト/プレイヤー） ---
all_sprites = None
enemies = None
bosses = None
bullets = None
rifles = None
mgs = None
shields = None
armys = None
player = None
# --- クラス ---
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        player_img = pygame.image.load(PLAYER_IMG_PATH).convert_alpha()
        self.image = pygame.transform.scale(player_img, (70, 70))
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 20
        self.speed_x = 0
        self.shot_delay = SHOT_DELAY_DEFAULT

    def update(self):
        self.speed_x = 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.speed_x = -8
        if keys[pygame.K_RIGHT]:
            self.speed_x = 8
        self.rect.x += self.speed_x
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        all_sprites.add(bullet)
        bullets.add(bullet)