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

class Shield(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        img = pygame.image.load(SHIELD_IMG_PATH).convert_alpha()
        self.image = pygame.transform.scale(img, (70, 70))
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(260, 380)
        self.rect.y = random.randrange(240, 260)
        self.speed_y = 1
        # カウンター（3発でArmyを増やす）
        self.max_hp = 0
        self.hp = self.max_hp

    def take_damage(self, amount=1):
        self.hp += amount

    def draw_hp_text(self, surface):
        font = pygame.font.Font(None, 18)
        txt = font.render(f"{max(self.hp,0)}", True, WHITE)
        txtr = txt.get_rect()
        txtr.midbottom = (self.rect.centerx, self.rect.top - 4)
        surface.blit(txt, txtr)

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > HEIGHT + 5:
            self.rect.x = random.randrange(260, 380)
            self.rect.y = random.randrange(240, 260)
            self.speed_y = 1

class Army(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        img = pygame.image.load(ARMY_IMG_PATH).convert_alpha()
        self.image = pygame.transform.scale(img, (70, 70))
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 20
        self.speed_x = 0
        self.shot_delay = SHOT_DELAY_DEFAULT  # 個別の連射レート
        self._last_shot_time = 0              # 個別の射撃タイマー

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

    def try_auto_shoot(self, now_ms: int):
        if now_ms - self._last_shot_time > self.shot_delay:
            self._last_shot_time = now_ms
            bullet = Bullet(self.rect.centerx, self.rect.top)
            all_sprites.add(bullet)
            bullets.add(bullet)

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        img = pygame.image.load(ENEMY_IMG_PATH).convert_alpha()
        self.image = pygame.transform.scale(img, (40, 40))
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(260, 380)
        self.rect.y = random.randrange(200, 220)
        self.speed_y = 1

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > HEIGHT + 5:
            self.rect.x = random.randrange(260, 380)
            self.rect.y = random.randrange(240, 260)
            self.speed_y = 1

class Boss(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        img = pygame.image.load(BOSS_IMG_PATH).convert_alpha()
        self.image = pygame.transform.scale(img, (100, 100))
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(260, 380)
        self.rect.y = random.randrange(240, 260)
        self.speed_y = 1
        self.max_hp = 6
        self.hp = self.max_hp

    def take_damage(self, amount=1):
        self.hp -= amount
        if self.hp <= 0:
            self.kill()

    def draw_hp_bar(self, surface):
        bar_w = self.rect.width
        bar_h = 6
        x = self.rect.x
        y = self.rect.y - 10
        pygame.draw.rect(surface, (0, 0, 0), (x, y, bar_w, bar_h))
        if self.max_hp > 0:
            fill_w = int(bar_w * max(self.hp, 0) / self.max_hp)
            pygame.draw.rect(surface, (0, 255, 0), (x, y, fill_w, bar_h))

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > HEIGHT + 5:
            self.rect.x = random.randrange(260, 380)
            self.rect.y = random.randrange(240, 260)
            self.speed_y = 1

class Rifle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        img = pygame.image.load(RIFLE_IMG_PATH).convert_alpha()
        self.image = pygame.transform.scale(img, (70, 70))
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(260, 380)
        self.rect.y = random.randrange(240, 260)
        self.speed_y = 1
        self.max_hp = 4
        self.hp = self.max_hp

    def take_damage(self, amount=1):
        self.hp -= amount
        if self.hp <= 0:
            self.kill()

    def draw_hp_text(self, surface):
        font = pygame.font.Font(None, 18)
        txt = font.render(f"{max(self.hp,0)}", True, WHITE)
        txtr = txt.get_rect()
        txtr.midbottom = (self.rect.centerx, self.rect.top - 4)
        surface.blit(txt, txtr)

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > HEIGHT + 5:
            self.rect.x = random.randrange(260, 380)
            self.rect.y = random.randrange(240, 260)
            self.speed_y = 1

class Mg(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        img = pygame.image.load(MG_IMG_PATH).convert_alpha()
        self.image = pygame.transform.scale(img, (70, 70))
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(260, 380)
        self.rect.y = random.randrange(240, 260)
        self.speed_y = 1.25
        self.max_hp = 12
        self.hp = self.max_hp

    def take_damage(self, amount=1):
        self.hp -= amount
        if self.hp <= 0:
            self.kill()

    def draw_hp_text(self, surface):
        font = pygame.font.Font(None, 18)
        txt = font.render(f"{max(self.hp,0)}", True, WHITE)
        txtr = txt.get_rect()
        txtr.midbottom = (self.rect.centerx, self.rect.top - 4)
        surface.blit(txt, txtr)

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > HEIGHT + 5:
            self.rect.x = random.randrange(260, 380)
            self.rect.y = random.randrange(240, 260)
            self.speed_y = 1

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 20))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed_y = -15

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.bottom < 0:
            self.kill()

# --- ユーティリティ ---
def draw_text(surface, text, size, x, y, color=WHITE):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.topleft = (x, y)
    surface.blit(text_surface, text_rect)

def spown():
    """スプライトグループと初期配置を作成（グローバルに代入）"""
    global all_sprites, enemies, bosses, bullets, rifles, mgs, shields, armys, player

    all_sprites = pygame.sprite.Group()
    enemies     = pygame.sprite.Group()
    bosses      = pygame.sprite.Group()
    bullets     = pygame.sprite.Group()
    rifles      = pygame.sprite.Group()
    mgs         = pygame.sprite.Group()
    shields     = pygame.sprite.Group()
    armys       = pygame.sprite.Group()

    player = Player()
    all_sprites.add(player)

    for _ in range(9):
        e = Enemy()
        all_sprites.add(e)
        enemies.add(e)

    sh = Shield()
    all_sprites.add(sh)
    shields.add(sh)

    boss = Boss()
    all_sprites.add(boss)
    bosses.add(boss)

    rf = Rifle()
    all_sprites.add(rf)
    rifles.add(rf)
    # Mg は最初は出さない

# --- メイン ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("ディフェンスショット VGAエディション")
    bg = pygame.image.load(BACKGROUND_IMG_PATH).convert()
    rect_bg = bg.get_rect()
    clock = pygame.time.Clock()
    pygame.font.init()

    spown()  # グループ初期化

    last_player_shot_time = pygame.time.get_ticks()
    running = True
    score = 0
    game_clear = False
    clear_start_time = None

    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                player.shot_delay = SHOT_DELAY_DEFAULT
                armys.shot_delay = SHOT_DELAY_DEFAULT

        # クリア演出中
        if game_clear:
            screen.blit(bg, rect_bg)
            draw_text(screen, "PHASE CLEAR", 50, WIDTH//2 - 120, 200, (255, 255, 0))
            pygame.display.flip()
            if pygame.time.get_ticks() - clear_start_time > 4000:
                game_clear = False
                spown()
            continue  # クリア演出中は他更新を止める

        # --- 自動射撃 ---
        now = pygame.time.get_ticks()
        if now - last_player_shot_time > player.shot_delay:
            last_player_shot_time = now
            player.shoot()

        # Army も自動射撃（各自の shot_delay で）
        for a in list(armys):
            a.try_auto_shoot(now)

        # --- 更新 ---
        all_sprites.update()

        # --- 当たり判定 ---
        # 敵
        hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
        if hits:
            score += 100 * len(hits)

        # シールド接触（プレイヤーが触れたら Army 追加）
        if pygame.sprite.spritecollide(player, shields, False):
            a = Army()
            all_sprites.add(a)
            armys.add(a)

        # シールドに弾が当たる（3発で Army 追加、カウンタリセット）
        shield_hits = pygame.sprite.groupcollide(shields, bullets, False, True)
        for sh in shield_hits:
            sh.take_damage(1)
            if sh.hp >= 3:
                a = Army()
                all_sprites.add(a)
                armys.add(a)
                sh.hp = 0

        # Boss
        boss_hits = pygame.sprite.groupcollide(bosses, bullets, False, True)
        for b in boss_hits:
            b.take_damage(1)
            if b.hp <= 0:
                score += 500

        # Rifle 撃破時：連射力UP + Mg 生成
        rifle_hits = pygame.sprite.groupcollide(rifles, bullets, False, True)
        for rf in rifle_hits:
            rf.take_damage(1)
            if rf.hp <= 0:
                score += 200
                player.shot_delay = SHOT_DELAY_RIFLE
                # すでにいる Army 全員の連射力も更新
                for a in armys:
                    a.shot_delay = SHOT_DELAY_RIFLE
                # Mg を出す
                mg = Mg()
                all_sprites.add(mg)
                mgs.add(mg)

        # Mg 撃破時：さらに連射力UP
        mg_hits = pygame.sprite.groupcollide(mgs, bullets, False, True)
        for mg in mg_hits:
            mg.take_damage(1)
            if mg.hp <= 0:
                score += 300
                player.shot_delay = SHOT_DELAY_MG
                for a in armys:
                    a.shot_delay = SHOT_DELAY_MG

        # --- 描画 ---
        screen.blit(bg, rect_bg)
        all_sprites.draw(screen)

        for b in bosses:
            b.draw_hp_bar(screen)
        for r in rifles:
            r.draw_hp_text(screen)
        for m in mgs:
            m.draw_hp_text(screen)
        for sh in shields:
            sh.draw_hp_text(screen)

        # スコア（1回だけ描画）
        draw_text(screen, f"Score: {score}", 24, 10, 10)

        pygame.display.flip()

        # --- クリア判定 ---
        if (len(enemies) == 0 and len(bosses) == 0 and
            len(rifles) == 0 and len(mgs) == 0 and not game_clear):
            game_clear = True
            clear_start_time = pygame.time.get_ticks()

    pygame.quit()

if __name__ == "__main__":
    main()
