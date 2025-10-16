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

import pygame
import sys
import random
import os

# --- 定数 ---
# 画面のサイズ
WIDTH = 320
HEIGHT = 240
# 色の定義 (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
# ゲームのフレームレート
FPS = 30

# 弾の発射間隔 (ミリ秒)
SHOT_DELAY_DEFAULT = 250   # 4発/秒
SHOT_DELAY_RIFLE   = 125   # 8発/秒
SHOT_DELAY_MG      = 67    # 15発/秒

# 実行ファイルのパスを取得
BASE_PATH = os.path.dirname(os.path.abspath(__file__))

# 音声ファイルパス
#MUSIC_FILE_PATH = BASE_PATH + "/Sound/sample.mp3"

#　スプライトの画像パス
ENEMY_IMG_PATH = BASE_PATH + "/Images/enemy.png"
BOSS_IMG_PATH = BASE_PATH + "/Images/boss.png"
PLAYER_IMG_PATH = BASE_PATH + "/Images/player.png"
ARMY_IMG_PATH = BASE_PATH + "/Images/army.png"
MG_IMG_PATH = BASE_PATH + "/Images/mg.png"
RIFLE_IMG_PATH = BASE_PATH + "/Images/rifle.png"
SHIELD_IMG_PATH = BASE_PATH + "/Images/shield.png"

# 背景の画像ファイルパス
BACKGROUND_IMG_PATH = BASE_PATH + "/Images/bg.png"

#変数
menu_play_over = 0
selected_firearm = 0


# --- クラスの定義 ---

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        player_img = pygame.image.load(PLAYER_IMG_PATH).convert_alpha()
        self.image = pygame.transform.scale(player_img, (35, 35))
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 20
        self.speed_x = 0
        # ★現在の発射間隔
        self.shot_delay = SHOT_DELAY_DEFAULT


    def update(self):
        """ プレイヤーの状態を毎フレーム更新する """
        self.speed_x = 0
        # 押されているキーを取得
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.speed_x = -8
        if keys[pygame.K_RIGHT]:
            self.speed_x = 8
        
        # 速度に応じて位置を更新
        self.rect.x += self.speed_x

        # プレイヤーが画面外に出ないように制御
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

    def shoot(self):
        """ 弾を発射する """
        bullet = Bullet(self.rect.centerx, self.rect.top)
        all_sprites.add(bullet)
        bullets.add(bullet)

class Shield(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        Shield_img = pygame.image.load(SHIELD_IMG_PATH).convert_alpha()
        self.image = pygame.transform.scale(Shield_img, (35, 35))
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(130, 190)
        self.rect.y = 120
        self.speed_y = 1
        # HP
        self.max_hp = 0
        self.hp = self.max_hp

    def take_damage(self, amount=1):
        self.hp += amount

    def draw_hp_text(self, surface):
        # 「軍を増やす数」を頭上中央に表示
        font = pygame.font.Font(None, 18)
        txt = font.render(f"{max(self.hp,0)}", True, WHITE)
        txtr = txt.get_rect()
        txtr.midbottom = (self.rect.centerx, self.rect.top - 4)
        # 読みやすさ向上の薄影
        surface.blit(txt, txtr)

      

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > HEIGHT + 5:
            self.rect.x = random.randrange(130, 190)
            self.rect.y = 120
            self.speed_y = 1

class Army(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        army_img = pygame.image.load(ARMY_IMG_PATH).convert_alpha()
        self.image = pygame.transform.scale(army_img, (35, 35))
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 20
        self.speed_x = 0
        # ★現在の発射間隔
        self.shot_delay = SHOT_DELAY_DEFAULT


    def update(self):
        """ プレイヤーの状態を毎フレーム更新する """
        self.speed_x = 0
        # 押されているキーを取得
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.speed_x = -8
        if keys[pygame.K_RIGHT]:
            self.speed_x = 8
        
        # 速度に応じて位置を更新
        self.rect.x += self.speed_x

        # プレイヤーが画面外に出ないように制御
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

    def shoot(self):
        """ 弾を発射する """
        bullet = Bullet(self.rect.centerx, self.rect.top)
        all_sprites.add(bullet)
        bullets.add(bullet)

class Enemy(pygame.sprite.Sprite):
    """ 敵キャラクターを管理するクラス """
    def __init__(self):
        super().__init__()
        # 敵の外観を作成
        enemy_img = pygame.image.load(ENEMY_IMG_PATH).convert_alpha()
        self.image = pygame.transform.scale(enemy_img, (20, 20))
        # 敵の位置とサイズを取得
        self.rect = self.image.get_rect()
        # 敵の初期位置をランダムに設定 (画面上部)
        self.rect.x = random.randrange(130, 190)
        self.rect.y = 120
        # 敵の落下速度をランダムに設定
        self.speed_y = 1

    def update(self):
        """ 敵の状態を毎フレーム更新する """
        # 速度に応じて位置を更新 (落下させる)
        self.rect.y += self.speed_y
        # 敵が画面下まで到達したら、出現させる
        if self.rect.top > HEIGHT + 5:
            self.rect.x = random.randrange(130, 190)
            self.rect.y = 120
            self.speed_y = 1

class Boss(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        Boss_img = pygame.image.load(BOSS_IMG_PATH).convert_alpha()
        self.image = pygame.transform.scale(Boss_img, (50, 50))
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(130, 190)
        self.rect.y = 120
        self.speed_y = 1
        # HP
        self.max_hp = 6
        self.hp = self.max_hp

    def take_damage(self, amount=1):
        self.hp -= amount
        if self.hp <= 0:
            self.kill()

    def draw_hp_bar(self, surface):
        # バーサイズ
        bar_w = self.rect.width
        bar_h = 6
        x = self.rect.x
        y = self.rect.y - 10
        # 背景
        pygame.draw.rect(surface, (0, 0, 0), (x, y, bar_w, bar_h))
        # 残量
        if self.max_hp > 0:
            fill_w = int(bar_w * max(self.hp, 0) / self.max_hp)
            pygame.draw.rect(surface, (0, 255, 0), (x, y, fill_w, bar_h))

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > HEIGHT + 5:
            self.rect.x = random.randrange(130, 190)
            self.rect.y = 120
            self.speed_y = 1



class Rifle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        Rifle_img = pygame.image.load(RIFLE_IMG_PATH).convert_alpha()
        self.image = pygame.transform.scale(Rifle_img, (35, 35))
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(130, 190)
        self.rect.y = 120
        self.speed_y = 1
        # HP
        self.max_hp = 4
        self.hp = self.max_hp

    def take_damage(self, amount=1):
        self.hp -= amount
        if self.hp <= 0:
            self.kill()

    def draw_hp_text(self, surface):
        # 「残りHP」を頭上中央に表示
        font = pygame.font.Font(None, 18)
        txt = font.render(f"{max(self.hp,0)}", True, WHITE)
        txtr = txt.get_rect()
        txtr.midbottom = (self.rect.centerx, self.rect.top - 4)
        # 読みやすさ向上の薄影
        surface.blit(txt, txtr)

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > HEIGHT + 5:
            self.rect.x = random.randrange(130, 190)
            self.rect.y = 120
            self.speed_y = 1



class Mg(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        mg_img = pygame.image.load(MG_IMG_PATH).convert_alpha()
        self.image = pygame.transform.scale(mg_img, (35, 35))
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(130, 190)
        self.rect.y = 120
        self.speed_y = 1.25
        # HP
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
            self.rect.x = random.randrange(130, 190)
            self.rect.y = 120
            self.speed_y = 1


class Bullet(pygame.sprite.Sprite):
    """ 弾を管理するクラス """
    def __init__(self, x, y):
        super().__init__()
        # 弾の外観を作成 (白色の小さな四角形)
        self.image = pygame.Surface((2, 10))
        self.image.fill(WHITE)
        # 弾の位置とサイズを取得
        self.rect = self.image.get_rect()
        # 弾の初期位置をプレイヤーの位置に設定
        self.rect.centerx = x
        self.rect.bottom = y
        # 弾の速度を設定
        self.speed_y = -15

    def update(self):
        """ 弾の状態を毎フレーム更新する """
        # 速度に応じて位置を更新 (上昇させる)
        self.rect.y += self.speed_y
        # 弾が画面外に出たら、自動的に消滅させる
        if self.rect.bottom < 0:
            self.kill()

# --- テキスト描画用の関数 --- # << 追加
def draw_text(surface, text, size, x, y, color=WHITE):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.topleft = (x, y)
    surface.blit(text_surface, text_rect)
 
# --- ゲームの初期化 ---
pygame.init()
# 画面とキャプションを設定
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ディフェンスショット VGAエディション")
screen = pygame.display.get_surface()
# 背景画像の取得
bg = pygame.image.load(BACKGROUND_IMG_PATH).convert_alpha()
rect_bg = bg.get_rect()


# フレームレート制御のための時計を作成
clock = pygame.time.Clock()

start_ticks = pygame.time.get_ticks()

current_ticks = pygame.time.get_ticks()
elapsed_ms = current_ticks - start_ticks
elapsed_sec = elapsed_ms // 1000  # 秒単位に変換

pygame.font.init() # << 追加 (フォントを使うために必要)

# --- スプライトグループの作成 ---
# 全てのキャラクターを管理するグループ
all_sprites = pygame.sprite.Group()
# --- ゲームオブジェクトの生成 ---

# --- スプライトグループの作成 ---
# 全てのキャラクターを管理するグループ
all_sprites = pygame.sprite.Group()
# 敵キャラクターを管理するグループ
enemies = pygame.sprite.Group()
#ボスキャラを管理するグループ
bosses = pygame.sprite.Group()
# 弾を管理するグループ
bullets = pygame.sprite.Group()

rifles = pygame.sprite.Group()

mgs = pygame.sprite.Group()

shields = pygame.sprite.Group()

armys = pygame.sprite.Group()
# --- ゲームオブジェクトの生成 ---

player = Player()
all_sprites.add(player)



# 敵
for i in range(9):
    enemy = Enemy()
    all_sprites.add(enemy)
    enemies.add(enemy)

shield = Shield()
all_sprites.add(shield)
shields.add(shield)

# Boss
boss = Boss()
all_sprites.add(boss)
bosses.add(boss)

# Rifle（最初から出す）
rifle = Rifle()
all_sprites.add(rifle)
rifles.add(rifle)


# ★ Mg はまだ出さない
# mg = Mg()
# all_sprites.add(mg)
# mgs.add(mg)

# --- ゲームループ ---
# 最後に弾を撃った時刻を記録する変数
# --- ゲームループ ---
last_shot_time = pygame.time.get_ticks()
last_army_shot_time = pygame.time.get_ticks()  # Army用の発射タイマー
running = True
score = 0 # << 追加: スコア用の変数

# 音楽ファイルの読み込み
#pygame.mixer.music.load(MUSIC_FILE_PATH)
#pygame.mixer.music.set_volume(1.0)

# 音楽の再生
#pygame.mixer.music.play(-1)  # 無限ループで再生
# --- ゲームの初期化 ---
pygame.init()
# 画面とキャプションを設定
info = pygame.display.Info()
SCREEN_WIDTH, SCREEN_HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN | pygame.SCALED)
pygame.display.set_caption("シンプルシューティング")
# 背景画像の取得
bg = pygame.image.load(BACKGROUND_IMG_PATH).convert_alpha()
rect_bg = bg.get_rect()


# フレームレート制御のための時計を作成
clock = pygame.time.Clock()

start_ticks = pygame.time.get_ticks()

current_ticks = pygame.time.get_ticks()
elapsed_ms = current_ticks - start_ticks
elapsed_sec = elapsed_ms // 1000  # 秒単位に変換

pygame.font.init() # << 追加 (フォントを使うために必要)

def format_time(ms):
    """ミリ秒を mm:ss に変換"""
    seconds = ms // 1000
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes:02}:{seconds:02}"

def main():
    last_shot_time = pygame.time.get_ticks()
    last_army_shot_time = pygame.time.get_ticks()  # ★Army用も初期化
    running = True
    score = 0
    game_clear = False
    clear_start_time = None
    start_ticks = pygame.time.get_ticks()

    # 音楽ファイルの読み込み
    #pygame.mixer.music.load(MUSIC_FILE_PATH)
    #pygame.mixer.music.set_volume(1.0)

    # 音楽の再生
    #pygame.mixer.music.play(-1)  # 無限ループで再生

    while running:
        # フレームレートを維持
        clock.tick(FPS)

        # --- イベント処理 ---
        for event in pygame.event.get():
            # ウィンドウの閉じるボタンが押されたらループを終了
            if event.type == pygame.QUIT:
                running = False

        elapsed_ms = pygame.time.get_ticks() - start_ticks
        

        # ★ゲームクリア中の処理
        if game_clear:
            screen.blit(bg, rect_bg)
            draw_text(screen, "GAME CLEAR", 50, WIDTH//2 - 120, 120, (255, 255, 0))  # 黄色
            pygame.display.flip()
            if pygame.time.get_ticks() - clear_start_time > 8000:
                running = False
            continue

        # ループの最初にある方（Mg生成あり）
        rifle_hits = pygame.sprite.groupcollide(rifles, bullets, False, True)
        for rifle in rifle_hits:
            rifle.take_damage(1)
            if rifle.hp <= 0:
                score += 200
                player.shot_delay = SHOT_DELAY_RIFLE
                army.shot_delay
                # ★Mgを出す
                mg = Mg()
                all_sprites.add(mg)
                mgs.add(mg)

                # ▼▼▼ 自動発射の処理を追加 ▼▼▼
                # 現在の時刻を取得
        # ▼▼▼ Player 自動発射処理 ▼▼▼
        now = pygame.time.get_ticks()

        # プレイヤーの自動発射
        if now - last_shot_time > player.shot_delay:
            last_shot_time = now
            player.shoot()

        # Army の自動発射
        if now - last_army_shot_time > player.shot_delay:  # Armyもプレイヤーと同じ間隔で撃つ
            last_army_shot_time = now
            for army in armys:
                army.shoot()


        # --- ゲームロジックの更新 ---
        # 全てのスプライトの状態を更新
        all_sprites.update()

        # 当たり判定 (弾と敵)
        # groupcollideは、衝突したスプライトを両方のグループから削除する
        # 最初のTrueは敵グループから、二番目のTrueは弾グループから削除することを意味する
        # 通常敵は従来通り：当たったら消える
        hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
        for _ in hits:
            score += 100
        
        # プレイヤーとシールドの接触（触れたら軍を追加）
        shielded = pygame.sprite.spritecollide(player, shields, False)
        for shield in shielded:
            army = Army()
            all_sprites.add(army)
            armys.add(army)

        # シールドと弾の衝突判定（弾を消してHPカウントアップ）
        shield_hits = pygame.sprite.groupcollide(shields, bullets, False, True)
        for shield in shield_hits:  
            shield.take_damage(1)
            if shield.hp >= 3:  # 3回当たったらArmyを生成
                army = Army()
                all_sprites.add(army)
                armys.add(army)
                shield.hp = 0  # カウンターリセット


        # Boss：弾は消える、Bossは残る → 当たった分だけHP減少
        boss_hits = pygame.sprite.groupcollide(bosses, bullets, False, True)
        for boss in boss_hits:
            boss.take_damage(1)
            if boss.hp <= 0:
                score += 500


        # Mg 撃破時
        mg_hits = pygame.sprite.groupcollide(mgs, bullets, False, True)
        for mg in mg_hits:
            mg.take_damage(1)
            if mg.hp <= 0:
                score += 300
                player.shot_delay = SHOT_DELAY_MG
                army.shot_delay = SHOT_DELAY_MG


        # 敵が倒されたら、ポイントを追加
        for hit in hits:
            score += 100 # << 追加: 敵を倒したら100点加算
            
        # --- 描画処理 ---
        # 画面を背景画像にする
        screen.blit(bg, rect_bg)
        # 全てのスプライトを描画
        all_sprites.draw(screen)

        # Boss はバー表示
        for b in bosses:
            b.draw_hp_bar(screen)

        # Rifle / Mg は数値表示
        for r in rifles:
            r.draw_hp_text(screen)
        for m in mgs:
            m.draw_hp_text(screen)

        # 経過時間
        # 経過時間表示
        draw_text(screen, f"Time: {format_time(elapsed_ms)}", 40, 10, 60, (0, 255, 0))

        # ▼▼▼ スコア表示処理を追加 ▼▼▼
        draw_text(screen, f"Score: {score}", 50, 10, 10)
        # ▲▲▲ ここまで追加 ▲▲▲
        # 画面を更新して描画内容を反映
        pygame.display.flip()

        # --- ゲームクリア判定 ---
        
        if (len(enemies) == 0 and len(bosses) == 0 
            and len(rifles) == 0 and len(mgs) == 0 
            and not game_clear):
            game_clear = True
            clear_start_time = pygame.time.get_ticks()

    # --- ゲーム終了処理 ---
    sys.exit()
    return

if __name__ == "__main__":
    main()