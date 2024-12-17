import os
import sys
import pygame as pg
import random

os.chdir(os.path.dirname(os.path.abspath(__file__)))

def generate_maze(rows, cols):
    """9×9の迷路を生成する関数"""
    maze = [[1 for _ in range(cols)] for _ in range(rows)]  # 迷路を壁で初期化
    start_x, start_y = 1, 1  # 開始地点
    stack = [(start_x, start_y)]  # 探索用スタック
    maze[start_y][start_x] = 0  # 開始地点を通路に

    directions = [(0, -2), (0, 2), (-2, 0), (2, 0)]  # 上下左右の移動方向

    while stack:
        x, y = stack[-1]
        random.shuffle(directions)  # 移動方向をランダムにする
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 1 <= nx < cols - 1 and 1 <= ny < rows - 1 and maze[ny][nx] == 1:
                maze[ny][nx] = 0
                maze[y + dy // 2][x + dx // 2] = 0  # 壁を壊して通路をつなげる
                stack.append((nx, ny))
                break
        else:
            stack.pop()
    return maze

def battle_scene(screen):
    """戦闘シーン"""
    font = pg.font.Font(None, 74)
    enemy_hp = 1  # 敵のHP
    player_attack = 100  # プレイヤーの攻撃力

    # 戦闘画面のループ
    while True:
        screen.fill((255, 0, 0))  # 戦闘背景は赤色
        text = font.render(f"敵のHP: {enemy_hp}", True, (255, 255, 255))
        screen.blit(text, (200, 250))

        pg.display.update()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:  # スペースキーで攻撃
                    enemy_hp -= player_attack
                    if enemy_hp <= 0:
                        return  # 戦闘終了

def main():
    pg.display.set_caption("はばたけ！こうかとん")
    screen = pg.display.set_mode((800, 600))
    clock = pg.time.Clock()
    cell_size = 50
    rows, cols = 9, 9

    # 初期迷路生成
    maze = generate_maze(rows, cols)
    goal_x, goal_y = cols - 2, rows - 2  # ゴール（青マス）の位置

    # キャラクター初期位置
    char_x, char_y = 1, 1

    # 敵の初期位置
    enemy_x, enemy_y = random.choice([(x, y) for y in range(1, rows, 2) for x in range(1, cols, 2) if (x, y) != (1, 1)])

    # 画像ロード
    bg_img = pg.image.load("fig/pg_bg.jpg")
    char_img = pg.transform.flip(pg.image.load("fig/3.png"), True, False)  # 左向き
    enemy_img = pg.image.load("fig/alien1.png")

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return

        # キー入力処理
        keys = pg.key.get_pressed()
        dx, dy = 0, 0
        if keys[pg.K_LEFT] and maze[char_y][char_x - 1] == 0:
            dx = -1
        if keys[pg.K_RIGHT] and maze[char_y][char_x + 1] == 0:
            dx = 1
        if keys[pg.K_UP] and maze[char_y - 1][char_x] == 0:
            dy = -1
        if keys[pg.K_DOWN] and maze[char_y + 1][char_x] == 0:
            dy = 1

        # キャラクターの移動
        char_x += dx
        char_y += dy

        # 敵と接触した場合、戦闘シーンへ
        if char_x == enemy_x and char_y == enemy_y:
            battle_scene(screen)  # 戦闘シーンへ
            # 戦闘終了後、敵を消し、キャラクターはその場所に戻る
            enemy_x, enemy_y = -1, -1  # 敵を無効な位置に設定

        # ゴールに到達した場合、新しい迷路生成
        if char_x == goal_x and char_y == goal_y:
            print("ゴール！新しい迷路を生成します")
            maze = generate_maze(rows, cols)
            char_x, char_y = 1, 1  # キャラクターの位置を初期化
            goal_x, goal_y = cols - 2, rows - 2  # 新しいゴール位置
            enemy_x, enemy_y = random.choice([(x, y) for y in range(1, rows, 2) for x in range(1, cols, 2)])

        # 画面描画
        screen.blit(bg_img, (0, 0))

        # 迷路の描画
        for y in range(rows):
            for x in range(cols):
                if maze[y][x] == 1:  # 壁
                    pg.draw.rect(screen, (0, 0, 0), (x * cell_size, y * cell_size, cell_size, cell_size))
                elif (x, y) == (goal_x, goal_y):  # ゴールマス（青色）
                    pg.draw.rect(screen, (0, 0, 255), (x * cell_size, y * cell_size, cell_size, cell_size))

        # 敵の描画
        if enemy_x != -1 and enemy_y != -1:
            screen.blit(enemy_img, (enemy_x * cell_size, enemy_y * cell_size))

        # キャラクターの描画
        screen.blit(char_img, (char_x * cell_size, char_y * cell_size))

        pg.display.update()
        clock.tick(10)

if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
