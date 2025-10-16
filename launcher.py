import os, sys, pygame, runpy, time, traceback, platform, subprocess

# 設定
EXE_DIR = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__))
GAMES_FOLDER = os.path.join(EXE_DIR, "games")
WIDTH, HEIGHT = 640, 480

def resource_path(relative_path):
    """exe化後でも正しくリソースを取得"""
    if hasattr(sys, "_MEIPASS"):
        # PyInstaller が一時展開したフォルダ
        base_path = sys._MEIPASS
    else:
        # 通常の Python 実行時はこのスクリプトのある場所を基準にする
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, relative_path)

def init_game():
    pygame.init()
    global screen, clock, font, menu_mode, sys_selected_index, font0, font1, font2, font3, font4, text_surface, is_language_menu, language_selected_index, text_rect, ICON_SIZE, ICON_SPACING, ICON_SELECTED_SCALE

    # 実スクリーン (仮想解像度640x480をSCALEDで拡大表示)
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN | pygame.SCALED)
    pygame.display.set_caption("RETRO IN PYGAME")
    clock = pygame.time.Clock()
    # フォントファイルのパスを取得
    font0_path   = resource_path("fonts/misaki_mincho.ttf")
    font1_path  = resource_path("fonts/misaki_mincho.ttf")
    font2_path  = resource_path("fonts/Evil Empire.otf")
    font3_path  = resource_path("fonts/ShipporiMincho-ExtraBold.ttf")
    font4_path  = resource_path("fonts/BusanFont_Provisional.ttf")

    # フォントオブジェクト生成
    font  = pygame.font.Font(font0_path, 60)
    font1 = pygame.font.Font(font1_path, 30)
    font2 = pygame.font.Font(font2_path, 30)
    font3 = pygame.font.Font(font3_path, 30)
    font4 = pygame.font.Font(font4_path, 30)
    text_surface = font.render("RETRO IN PYGAME", True, (30,144,255))
    text_rect = text_surface.get_rect(center=(WIDTH//2, HEIGHT//2))
    menu_mode = 0
    sys_selected_index = 0
    is_language_menu = False  # 言語メニュー表示中かどうか
    language_selected_index = 0
    ICON_SIZE = (HEIGHT // 4, HEIGHT // 4)
    ICON_SPACING = 40
    ICON_SELECTED_SCALE = 1.2

init_game()

# 起動音ファイルも同様に
sound_path = resource_path("sounds/start_up.mp3")
pygame.mixer.init()
pygame.mixer.music.load(sound_path)


# ゲーム一覧
games = []
for folder in os.listdir(GAMES_FOLDER):
    folder_path = os.path.join(GAMES_FOLDER, folder)
    main_py = os.path.join(folder_path, "main.py")
    main_bin = os.path.join(folder_path, "main.bin")
    main_exe = os.path.join(folder_path, "main.exe")
    icon_path = os.path.join(folder_path, "icon.png")

    game = {"name": folder, "main_path": None, "main_type": None, "icon": None}

    if os.path.isfile(main_py):
        game["main_path"] = main_py
        game["main_type"] = "py"
    elif os.path.isfile(main_bin):
        game["main_path"] = main_bin
        game["main_type"] = "bin"
    elif os.path.isfile(main_exe):
        game["main_path"] = main_exe
        game["main_type"] = "exe"

    if os.path.isfile(icon_path):
        icon = pygame.image.load(icon_path).convert_alpha()
        icon = pygame.transform.scale(icon, ICON_SIZE)
        game["icon"] = icon

    if game["main_path"]:
        games.append(game)

selected_index = 0

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
LANGUAGE_FILE = os.path.join(STORAGE_DIR, "language.txt")
def load_language():
    # 新ファイルを優先して読む
    try:
        with open(LANGUAGE_FILE, "r", encoding="utf-8") as f:
            s = f.read().strip()
            return s if s else "en"
    except Exception:
        # 旧ファイル（language.txt）を読む
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            legacy = os.path.join(script_dir, "language.txt")
            with open(legacy, "r", encoding="utf-8") as f:
                s = f.read().strip()
                return s if s else "en"
        except Exception:
            return "en"

sys_language = load_language()

def save_language(val: str):
    try:
        os.makedirs(STORAGE_DIR, exist_ok=True)
        tmp = LANGUAGE_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(val.strip())  # 言語コードをそのまま保存
        os.replace(tmp, LANGUAGE_FILE)
    except Exception as e:
        print("Save error:", e)



def shutdown():
    system = platform.system()
    if system == "Windows":
        os.system("shutdown /s /t 0")
    elif system == "Linux" or system == "Darwin":  # Darwin = macOS
        os.system("sudo shutdown -h now")
    else:
        print(f"{system} は未対応です")
        sys.exit(1)

def restart():
    system = platform.system()
    if system == "Windows":
        os.system("shutdown /r /t 0")
    elif system == "Linux" or system == "Darwin":
        os.system("sudo shutdown -r now")
    else:
        print(f"{system} は未対応です")
        sys.exit(1)

def draw_language_menu():
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(200)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))

    pygame.draw.rect(screen, (80, 80, 80), pygame.Rect(40, 30, 560, 420))
    pygame.draw.rect(screen, (255, 255, 0), pygame.Rect(40, 30, 560, 420), 3)

    language_options = [
        ("   X   ", font3),
        ("English(US)", font2),
        ("ﾆﾎﾝｺﾞ", font1),
        ("中文(繁體字)", font3),
        ("한국어", font4),
    ]

    for i, (text, font) in enumerate(language_options):
        # 選択中なら白背景＋黒文字に変更
        if i == language_selected_index:
            option_surface = font.render(text, True, (0, 0, 0))  # 黒文字
            bg_rect = pygame.Rect(
                WIDTH//2 - option_surface.get_width()//2 - 10,
                100 + i*50 - 5,
                option_surface.get_width() + 20,
                option_surface.get_height() + 10
            )
            pygame.draw.rect(screen, (255, 255, 255), bg_rect)  # 白背景
        else:
            option_surface = font.render(text, True, (200, 200, 200))  # 非選択は灰文字

        # 中央寄せで文字を配置
        screen.blit(option_surface, (WIDTH//2 - option_surface.get_width()//2, 100 + i*50))

    pygame.display.flip()


def apply_language_selection():
    global sys_language, is_language_menu
    if language_selected_index == 0:  # 閉じる
        is_language_menu = False
    elif language_selected_index == 1:
        sys_language = "en"; is_language_menu = False
        save_language(sys_language)
    elif language_selected_index == 2:
        sys_language = "ja"; is_language_menu = False
        save_language(sys_language)
    elif language_selected_index == 3:
        sys_language = "ch"; is_language_menu = False
        save_language(sys_language)
    elif language_selected_index == 4:
        sys_language = "ks"; is_language_menu = False
        save_language(sys_language)

    
# --- フェードイン関数 ---
def fade_in_text(text_surf, rect, duration=2.0):
    start_time = time.time()
    while True:
        now = time.time()
        elapsed = now - start_time
        alpha = min(255, int((elapsed / duration) * 255))

        # 半透明サーフェスを作る
        fade_surface = text_surf.copy()
        fade_surface.set_alpha(alpha)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill((0, 0, 0))
        screen.blit(fade_surface, rect)
        pygame.display.flip()
        clock.tick(60)

        if alpha >= 255:
            break

def draw_menu():
    global selected_index, sys_selected_index, menu_mode, sys_language

    screen.fill((4, 29, 0, 255))

    # タイトル
    if games:
        if sys_language == "en":
            language_font = font2
        elif sys_language == "ja":
            language_font = font1
        elif sys_language == "ch":
            language_font = font3
        elif sys_language == "ks":
            language_font = font4
        title = games[selected_index]["name"]
        title_surface = language_font.render(title, True, (255, 255, 0))
        screen.blit(title_surface, ((WIDTH - title_surface.get_width()) // 2, 30))

    # --- 上段：ゲームアイコン ---
    y = HEIGHT // 2 - ICON_SIZE[1] // 2
    center_x = WIDTH // 2 - ICON_SIZE[0] // 2

    for i, game in enumerate(games):
        dx = i - selected_index
        base_x = center_x + dx * (ICON_SIZE[0] + ICON_SPACING)
        icon = game["icon"]
        if not icon:
            continue

        if i == selected_index and menu_mode == 0:  # ゲーム選択中のみ枠を付ける
            scale = ICON_SELECTED_SCALE
            scaled_size = (int(ICON_SIZE[0] * scale), int(ICON_SIZE[1] * scale))
            offset = (
                (scaled_size[0] - ICON_SIZE[0]) // 2,
                (scaled_size[1] - ICON_SIZE[1]) // 2,
            )
            icon_scaled = pygame.transform.scale(icon, scaled_size)
            screen.blit(icon_scaled, (base_x - offset[0], y - offset[1]))
            pygame.draw.rect(
                screen,
                (255, 255, 0),
                (
                    base_x - offset[0] - 5,
                    y - offset[1] - 5,
                    scaled_size[0] + 10,
                    scaled_size[1] + 10,
                ),
                4,
            )
        else:
            screen.blit(icon, (base_x, y))

    # --- 下段：システムメニュー ---
    if sys_language == "en":
        sys_options = ["Relogin  ", "Shutdown  ", "  Restart", "  Language"]
    if sys_language == "ja":
        sys_options = [" GUIﾘｽﾀｰﾄ ", "  ﾊﾟﾜｰｵﾌ  ", "   ﾘｽﾀｰﾄ  ", "    ｹﾞﾝｺﾞ "]
    if sys_language == "ch":
        sys_options = [" 重新登入  ", "    關機     ", "重新啟動", "  語言  "]
    if sys_language == "ks":
        sys_options = [" 재로그인  ", "    종료     ", " 재시작 ", "  언어  "]
    sys_y = HEIGHT - 80
    spacing = 140
    start_x = (WIDTH - (len(sys_options) * spacing)) // 2

    for i, label in enumerate(sys_options):
        color = (255, 255, 0) if (i == sys_selected_index and menu_mode == 1) else (200, 200, 200)
        if sys_language == "ja":
            text_surface = font1.render(label, True, color)
        elif sys_language == "en":
            text_surface = font2.render(label, True, color)
        elif sys_language == "ch":
            text_surface = font3.render(label, True, color)
        elif sys_language == "ks":
            text_surface = font4.render(label, True, color)
        else:
            text_surface = font1.render(label, True, color)
        x = start_x + i * spacing
        screen.blit(text_surface, (x, sys_y))

    pygame.display.flip()

def handle_system_action(index):
    if index == 0:  # 再ログオン (pygame再起動)
        pygame.quit()
        os.execl(sys.executable, sys.executable, *sys.argv)

    elif index == 1:  # シャットダウン
        shutdown()

    elif index == 2:  # 再起動
        restart()
    elif index == 3:  # 言語
        global is_language_menu
        is_language_menu = True

def run_game(game):
    path = game["main_path"]
    game_dir = os.path.dirname(path)  # ゲームフォルダ

    try:
        if game["main_type"] == "py":
            # Python スクリプト
            current_dir = os.getcwd()
            try:
                os.chdir(game_dir)
                runpy.run_path(path, run_name="__main__")
            finally:
                os.chdir(current_dir)

        elif game["main_type"] in ("exe", "bin"):
            # バイナリ (Windows / Linux)
            subprocess.run([path], cwd=game_dir, check=False)

    except SystemExit:
        # sys.exit() は無視してランチャーに戻る
        pass
    except Exception:
        print("=== error 001 Game Exception ===")
        traceback.print_exc()
        print("=== Back Launcher ===")

    # ランチャーの Pygame 再初期化
    init_game()
# --- 実行 ---
# フェードインと同時に音を再生
pygame.mixer.music.play()
fade_in_text(text_surface, text_rect, duration=2.5)

while pygame.mixer.music.get_busy():
    pygame.time.delay(100)

run = True
def main():
    global selected_index, menu_mode, sys_selected_index, run, is_language_menu, language_selected_index
    while run:
        if is_language_menu:
            draw_menu()            # ← ランチャーを描画
            draw_language_menu()   # ← その上に言語選択を重ねる
        else:
            draw_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if is_language_menu:
                    if event.key == pygame.K_UP:
                        language_selected_index = (language_selected_index - 1) % 5
                    elif event.key == pygame.K_DOWN:
                        language_selected_index = (language_selected_index + 1) % 5
                    elif event.key == pygame.K_RETURN:
                        apply_language_selection()
                    elif event.key == pygame.K_SPACE:
                        is_language_menu = False

                elif menu_mode == 0:
                    if event.key == pygame.K_LEFT:
                        selected_index = (selected_index - 1) % len(games)
                    elif event.key == pygame.K_RIGHT:
                        selected_index = (selected_index + 1) % len(games)
                    elif event.key == pygame.K_RETURN:
                        run_game(games[selected_index])
                    elif event.key == pygame.K_DOWN:
                        menu_mode = 1

                elif menu_mode == 1:
                    if event.key == pygame.K_LEFT:
                        sys_selected_index = (sys_selected_index - 1) % 4
                    elif event.key == pygame.K_RIGHT:
                        sys_selected_index = (sys_selected_index + 1) % 4
                    elif event.key == pygame.K_UP:
                        menu_mode = 0
                    elif event.key == pygame.K_RETURN:
                        handle_system_action(sys_selected_index)

        clock.tick(30)

if __name__ == "__main__":
    main()
