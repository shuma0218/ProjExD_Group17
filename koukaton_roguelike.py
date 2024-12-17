import pygame
import random
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))
# Pygameの初期化
pygame.init()

# 画面サイズとマスの設定
WIDTH, HEIGHT = 540, 540
ROWS, COLS = 9, 9
CELL_SIZE = WIDTH // COLS

# 色の定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)  # 戦闘マス
GREEN = (0, 255, 0)  # 回復マス
BLUE = (0, 0, 255)  # 強化マス

# 画面の作成
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("9x9 Maze with Player")

# プレイヤー画像の読み込み
player_img = pygame.image.load(f"fig/5.png")
player_img = pygame.transform.scale(player_img, (CELL_SIZE, CELL_SIZE))

def generate_maze(rows, cols):
    """深さ優先探索を用いて迷路を生成"""
    maze = [[1 for _ in range(cols)] for _ in range(rows)]
    visited = [[False for _ in range(cols)] for _ in range(rows)]
    directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]

    def in_bounds(x, y):
        return 0 <= x < cols and 0 <= y < rows

    def carve_passages(cx, cy):
        visited[cy][cx] = True
        maze[cy][cx] = 0
        random.shuffle(directions)

        for dx, dy in directions:
            nx, ny = cx + dx * 2, cy + dy * 2
            if in_bounds(nx, ny) and not visited[ny][nx]:
                maze[cy + dy][cx + dx] = 0
                carve_passages(nx, ny)

    carve_passages(1, 1)
    return maze

def add_event_cells(maze):
    """イベントマスを配置"""
    event_cells = {'battle': [], 'heal': None, 'powerup': []}
    empty_cells = [(x, y) for y in range(ROWS) for x in range(COLS) if maze[y][x] == 0]

    num_battles = random.randint(3, 6)
    event_cells['battle'] = random.sample(empty_cells, num_battles)
    event_cells['heal'] = random.choice(empty_cells)
    num_powerups = random.randint(0, 2)
    event_cells['powerup'] = random.sample(empty_cells, num_powerups)

    return event_cells

def draw_maze(maze, events):
    """迷路とイベントマスを描画"""
    for y in range(ROWS):
        for x in range(COLS):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            if maze[y][x] == 1:  # 壁
                pygame.draw.rect(screen, BLACK, rect)
            else:
                pygame.draw.rect(screen, WHITE, rect)
                pygame.draw.rect(screen, BLACK, rect, 1)

    for x, y in events['battle']:
        pygame.draw.rect(screen, RED, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    if events['heal']:
        x, y = events['heal']
        pygame.draw.rect(screen, GREEN, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    for x, y in events['powerup']:
        pygame.draw.rect(screen, BLUE, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

def main():
    maze = generate_maze(ROWS, COLS)
    events = add_event_cells(maze)

    # プレイヤーの初期位置
    player_x, player_y = 1, 1

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        new_x, new_y = player_x, player_y

        # 移動処理
        if keys[pygame.K_UP]:
            new_y -= 1
        if keys[pygame.K_DOWN]:
            new_y += 1
        if keys[pygame.K_LEFT]:
            new_x -= 1
        if keys[pygame.K_RIGHT]:
            new_x += 1

        # 壁チェック: 移動先が道なら移動
        if 0 <= new_x < COLS and 0 <= new_y < ROWS and maze[new_y][new_x] == 0:
            player_x, player_y = new_x, new_y

        # 描画
        screen.fill(WHITE)
        draw_maze(maze, events)
        screen.blit(player_img, (player_x * CELL_SIZE, player_y * CELL_SIZE))
        pygame.display.flip()

    pygame.quit()

# 実行
main()
