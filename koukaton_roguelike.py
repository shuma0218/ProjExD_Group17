import os
import sys
import pygame as pg
import random

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 定数設定
WIDTH, HEIGHT = 11, 11  # 11x11マスで固定
CELL_SIZE = 40
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600

# 色の定義
WHITE = (255, 255, 255)
TRANSPARENT = (0, 0, 0, 0)
RED = (255, 0, 0)    # 戦闘マス
GREEN = (0, 255, 0)  # 回復マス
BLUE = (0, 0, 255)   # 強化マス
PURPLE = (128, 0, 128)  # ボスマス

# イベントマスの種類
EVENT_TYPES = {
    "battle": RED,
    "heal": GREEN,
    "buff": BLUE,
    "boss": PURPLE
}

# スキルクラス
class Skill:
    def __init__(self, name, mana_cost, effect):
        self.name = name        # スキル名
        self.mana_cost = mana_cost  # スキルのマナコスト
        self.effect = effect    # スキルの効果（関数などで実装可能）

# プレイヤーのスキルと敵のスキル共通のスキル候補
skill_pool = [
    Skill("Boost Attack", 5, lambda entity: setattr(entity, 'atk', entity.atk + 5)),
    Skill("Boost Defense", 5, lambda entity: setattr(entity, 'def_', entity.def_ + 5)),
    Skill("Increase Damage", 4, lambda target: setattr(target, 'def_', max(0, target.def_ - 5))),
    Skill("Double Strike", 6, lambda entity: setattr(entity, 'next_attack_double', True)),
    Skill("Life Steal", 8, lambda entity: setattr(entity, 'next_attack_heal', True)),
    Skill("Nullify Skill", 7, lambda entity: setattr(entity, 'nullify_next_skill', True))
]

# プレイヤークラス
class Player:
    def __init__(self, atk=10, def_=5, mp=20, hp=100):
        self.atk = atk  # 攻撃力
        self.def_ = def_  # 防御力
        self.mp = mp  # マナ
        self.hp = hp  # 体力
        self.skills = []  # 所持スキル
        self.init_skills()  # 初期スキルを設定
        self.next_attack_double = False  # 次の通常攻撃が二回攻撃になる
        self.next_attack_heal = False  # 次の通常攻撃で回復する
        self.nullify_next_skill = False  # 次の相手スキルを無効化

    def init_skills(self):
        # ランダムに1つスキルを選択して所持
        self.skills.append(random.choice(skill_pool))

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp < 0:
            self.hp = 0  # HPが0未満にならないように調整
        return self.hp
    
    def use_mana(self, amount):
        if self.mp >= amount:
            self.mp -= amount
            return True
        return False

    def normal_attack(self, target):
        damage = self.atk
        if self.next_attack_double:
            damage *= 2
            self.next_attack_double = False
        target.take_damage(damage)

        if self.next_attack_heal:
            self.hp += damage
            self.next_attack_heal = False

# 敵クラス
class Enemy:
    def __init__(self, atk, def_, hp):
        self.atk = atk  # 攻撃力
        self.def_ = def_  # 防御力
        self.hp = hp  # 体力（低めに設定）
        self.skills = random.sample(skill_pool, 2)  # 初期から2つのスキルをランダムに所持

    def take_damage(self, damage):
        reduced_damage = max(0, damage - self.def_)
        self.hp -= reduced_damage
        return self.hp

    def normal_attack(self, target):
        target.take_damage(self.atk)

# ボスクラス
class Boss:
    def __init__(self, atk=20, def_=15, hp=300):
        self.atk = atk  # 攻撃力（非常に高い）
        self.def_ = def_  # 防御力（非常に高い）
        self.hp = hp  # 体力（非常に高い）
        self.skills = random.sample(skill_pool, 5)  # 初期から5つのスキルをランダムに所持

    def take_damage(self, damage):
        reduced_damage = max(0, damage - self.def_)
        self.hp -= reduced_damage
        return self.hp

    def normal_attack(self, target):
        target.take_damage(self.atk)

# 敵のパターン定義
def generate_enemy_patterns():
    return [
        Enemy(atk=8, def_=3, hp=40),  # 攻撃型
        Enemy(atk=5, def_=6, hp=50),  # 防御型
        Enemy(atk=6, def_=4, hp=45),  # バランス型
        Enemy(atk=10, def_=2, hp=35), # 高火力型
        Enemy(atk=4, def_=7, hp=55)   # タンク型
    ]

# ボス生成関数
def generate_boss():
    return Boss()

# 迷路生成関数
def generate_maze(width, height):
    maze = [[1 for _ in range(width)] for _ in range(height)]
    stack = []

    # 初期位置
    start_x, start_y = 1, 1
    maze[start_y][start_x] = 0
    stack.append((start_x, start_y))

    # 移動方向
    directions = [(-2, 0), (2, 0), (0, -2), (0, 2)]

    while stack:
        x, y = stack[-1]
        random.shuffle(directions)
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 < nx < width and 0 < ny < height and maze[ny][nx] == 1:
                maze[ny][nx] = 0
                maze[y + dy // 2][x + dx // 2] = 0
                stack.append((nx, ny))
                break
        else:
            stack.pop()

    return maze

# イベントマス生成関数
def generate_event_tiles(maze):
    events = {}

    def place_event(event_type, count):
        placed = 0
        while placed < count:
            x, y = random.randint(1, WIDTH - 2), random.randint(1, HEIGHT - 2)
            if maze[y][x] == 0 and (x, y) not in events:
                if not any(abs(x - ex) + abs(y - ey) <= 2 for ex, ey in events if events[(ex, ey)] == event_type):
                    events[(x, y)] = event_type
                    placed += 1

    # 戦闘マス：3~5個を分散して配置
    place_event("battle", random.randint(3, 5))

    # 回復マス：1つのみ配置
    place_event("heal", 1)

    # 強化マス：2~3個を分散して配置
    place_event("buff", random.randint(2, 3))

    return events

# ボスマスを生成
def spawn_boss_tile(maze, events):
    while True:
        x, y = random.randint(1, WIDTH - 2), random.randint(1, HEIGHT - 2)
        if maze[y][x] == 0 and (x, y) not in events:
            events[(x, y)] = "boss"
            break

# プレイヤーの初期位置をランダムに設定
# イベントマスと被らないようにする
def get_random_start(maze, events):
    while True:
        x, y = random.randint(1, WIDTH - 2), random.randint(1, HEIGHT - 2)
        if maze[y][x] == 0 and (x, y) not in events:
            return x, y

# 描画関数
def draw_maze(screen, maze, bg_img, offset_x, offset_y, events):
    for y, row in enumerate(maze):
        for x, cell in enumerate(row):
            rect = (offset_x + x * CELL_SIZE, offset_y + y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            if cell == 0:  # 白い道のみ描画
                pg.draw.rect(screen, WHITE, rect)
            else:  # 壁部分は透明化
                screen.blit(bg_img, rect, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    for (x, y), event_type in events.items():
        color = EVENT_TYPES[event_type]
        rect = (offset_x + x * CELL_SIZE, offset_y + y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pg.draw.rect(screen, color, rect)

# プレイヤー描画関数
def draw_player(screen, player_img, player_pos, offset_x, offset_y):
    x, y = player_pos
    rect = (offset_x + x * CELL_SIZE, offset_y + y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    screen.blit(pg.transform.scale(player_img, (CELL_SIZE, CELL_SIZE)), rect)

def move_player(player_pos, direction, maze, events):
    x, y = player_pos
    dx, dy = direction
    new_x, new_y = x + dx, y + dy  # 移動後の位置を計算

    # 移動可能か確認
    if 0 <= new_x < WIDTH and 0 <= new_y < HEIGHT and maze[new_y][new_x] == 0:
        # イベントが存在する場合、対応する結果を返す
        if (new_x, new_y) in events:
            if events[(new_x, new_y)] == "battle":
                return "battle", new_x, new_y
            elif events[(new_x, new_y)] == "boss":
                return "boss", new_x, new_y
        return (new_x, new_y)  # 通常の移動結果を返す

    return player_pos  # 移動不可の場合、元の位置を返す

def start_battle(screen, player, enemy, ui_buttons, ui_area, log_area):
    battle_logs = []
    is_player_turn = True
    used_actions = {"attack": False, "skills": set()}  # 使用済みアクションを追跡

    while player.hp > 0 and enemy.hp > 0:
        screen.fill((0, 0, 0))  # 背景をリセット
        draw_battle_ui(screen, ui_buttons, ui_area, used_actions)  # UIの描画
        draw_battle_log(screen, log_area, battle_logs)  # バトルログの描画
        pg.display.update()

        if is_player_turn:
            action = decide_player_action(player, ui_buttons, used_actions)
            if action == "attack":
                enemy.take_damage(player.atk)
                battle_logs.append(f"Player attacks! Enemy HP: {enemy.hp}")
            elif isinstance(action, Skill):
                action.effect(enemy)
                battle_logs.append(f"Player used {action.name}!")
            elif action == "end_turn":
                is_player_turn = False  # 敵のターンに切り替え
                used_actions = {"attack": False, "skills": set()}  # 使用済みアクションをリセット
        else:
            # 敵のターン
            enemy_turn(enemy, player, battle_logs)
            is_player_turn = True  # プレイヤーのターンに切り替え

        pg.time.wait(500)  # 各ターン間の待機


def draw_battle_log(screen, log_area, logs):
    screen.fill((0, 0, 0), log_area)  # ログエリアを黒で塗りつぶす
    font = pg.font.Font(None, 24)
    for i, log in enumerate(logs[-5:]):  # 最新5件のログを表示
        log_surface = font.render(log, True, WHITE)
        screen.blit(log_surface, (log_area.left + 10, log_area.top + i * 20))

def decide_player_action(player, ui_buttons, used_actions):
    selected_action = None

    while selected_action is None:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:  # 左クリック
                mouse_pos = event.pos
                for button in ui_buttons:
                    if button["rect"].collidepoint(mouse_pos):
                        action = button["action"]
                        if action == "attack" and not used_actions["attack"]:
                            used_actions["attack"] = True
                            return "attack"
                        elif isinstance(action, Skill) and action not in used_actions["skills"]:
                            used_actions["skills"].add(action)
                            return action
                        elif action == "end_turn":
                            return "end_turn"


def create_battle_ui(player):
    ui_buttons = []
    ui_area = pg.Rect(20, 20, 160, WINDOW_HEIGHT - 40)

    # 通常攻撃ボタン
    attack_button = {
        "rect": pg.Rect(40, 50, 120, 40),
        "color": (200, 0, 0),
        "text": "通常攻撃",
        "action": "attack"
    }
    ui_buttons.append(attack_button)

    # スキルボタン
    for i, skill in enumerate(player.skills):
        skill_button = {
            "rect": pg.Rect(40, 120 + i * 60, 120, 40),
            "color": (0, 200, 0),
            "text": skill.name,
            "action": skill
        }
        ui_buttons.append(skill_button)

    # ターン終了ボタン
    end_turn_button = {
        "rect": pg.Rect(40, 400, 120, 40),
        "color": (0, 0, 200),
        "text": "ターン終了",
        "action": "end_turn"
    }
    ui_buttons.append(end_turn_button)

    return ui_buttons, ui_area

def draw_battle_ui(screen, ui_buttons, ui_area, used_actions):
    pg.draw.rect(screen, (50, 50, 50), ui_area)  # UI背景

    font = pg.font.Font(None, 24)
    for button in ui_buttons:
        color = button["color"]
        if button["action"] == "attack" and used_actions["attack"]:
            color = (100, 100, 100)  # 使用済みの通常攻撃は暗く表示
        elif isinstance(button["action"], Skill) and button["action"] in used_actions["skills"]:
            color = (100, 100, 100)  # 使用済みスキルは暗く表示

        pg.draw.rect(screen, color, button["rect"])
        text_surface = font.render(button["text"], True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=button["rect"].center)
        screen.blit(text_surface, text_rect)

def enemy_turn(enemy, player, battle_logs):
    if isinstance(enemy, Boss):
        # ボスのスキル使用
        skill = random.choice(enemy.skills)
        skill.effect(player)
        battle_logs.append(f"Boss used {skill.name}! Player HP: {player.hp}")

    # 敵のスキル使用
    if enemy.skills:
        skill = random.choice(enemy.skills)
        skill.effect(player)
        battle_logs.append(f"Enemy used {skill.name}! Player HP: {player.hp}")

    # 通常攻撃
    damage = max(0, enemy.atk - player.def_)
    player.take_damage(enemy.atk)
    battle_logs.append(f"{'Boss' if isinstance(enemy, Boss) else 'Enemy'} attacks! Player HP: {player.hp}")


def main():
    pg.display.set_caption("はばたけ！こうかとん")
    screen = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pg.time.Clock()
    bg_img = pg.image.load("fig/pg_bg.jpg")
    bg_img = pg.transform.scale(bg_img, (WINDOW_WIDTH, WINDOW_HEIGHT))  # 背景画像をウィンドウ全体に拡大

    player_img = pg.image.load("fig/3.png")  # プレイヤー画像をロード
    player = Player()  # プレイヤーのステータスを初期化

    while True:
        # 迷路生成
        maze = generate_maze(WIDTH, HEIGHT)
        events = generate_event_tiles(maze)

        # プレイヤーの初期位置
        player_pos = get_random_start(maze, events)

        # 迷路の描画位置を中央に計算
        offset_x = (WINDOW_WIDTH - WIDTH * CELL_SIZE) // 2
        offset_y = (WINDOW_HEIGHT - HEIGHT * CELL_SIZE) // 2

        boss_spawned = False

        tmr = 0
        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                if event.type == pg.KEYDOWN:
                    direction = None
                    if event.key == pg.K_UP:
                        direction = (0, -1)
                    elif event.key == pg.K_DOWN:
                        direction = (0, 1)
                    elif event.key == pg.K_LEFT:
                        direction = (-1, 0)
                    elif event.key == pg.K_RIGHT:
                        direction = (1, 0)

                    if direction:
                        result = move_player(player_pos, direction, maze, events)

                        if isinstance(result, tuple):  # 移動成功時またはイベント発生時
                            if result[0] == "battle":
                                new_x, new_y = result[1], result[2]
                                enemy = random.choice(generate_enemy_patterns())
                                log_area = pg.Rect(200, WINDOW_HEIGHT - 100, WINDOW_WIDTH - 200, 100)
                                ui_buttons, ui_area = create_battle_ui(player)
                                start_battle(screen, player, enemy, ui_buttons, ui_area, log_area)
                                del events[(new_x, new_y)]  # 戦闘マスを削除
                            elif result[0] == "boss":
                                new_x, new_y = result[1], result[2]
                                boss = Boss()
                                log_area = pg.Rect(200, WINDOW_HEIGHT - 100, WINDOW_WIDTH - 200, 100)
                                ui_buttons, ui_area = create_battle_ui(player)
                                start_battle(screen, player, boss, ui_buttons, ui_area, log_area)
                                del events[(new_x, new_y)]  # ボスマスを削除
                            else:
                                player_pos = result  # 通常移動時、プレイヤー位置を更新


            else:
                # 全ての戦闘マスを踏んだ場合にボスマスを生成
                if not boss_spawned and all(e != "battle" for e in events.values()):
                    spawn_boss_tile(maze, events)
                    boss_spawned = True

                screen.blit(bg_img, (0, 0))  # 背景画像をウィンドウ全体に表示
                draw_maze(screen, maze, bg_img, offset_x, offset_y, events)
                draw_player(screen, player_img, player_pos, offset_x, offset_y)
                pg.display.update()
                tmr += 1
                clock.tick(10)
                continue

            break




if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
