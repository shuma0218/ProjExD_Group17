import os
import sys
import random
import pygame as pg
os.chdir(os.path.dirname(os.path.abspath(__file__)))

class MapGenerator:
    """
    迷路とイベントマスを生成するクラス。
    """
    def __init__(self, width: int, height: int):
        """
        迷路の初期化を行う。
        :param width: 迷路の幅（マス単位、奇数）
        :param height: 迷路の高さ（マス単位、奇数）
        """
        self.width: int = width
        self.height: int = height
        self.map: list[list[int]] = [[1 for _ in range(width)] for _ in range(height)]  # 1: 壁, 0: 道
        self.event_tiles: list[tuple[tuple[int, int], str]] = []
        self.start_tile: tuple[int, int] = (1, 1)

    def generate_maze(self) -> None:
        """
        深さ優先探索を使って迷路を生成する。
        """
        def carve_passages(cx: int, cy: int) -> None:
            """
            迷路の通路を掘り進める関数。
            :param cx: 現在のx座標
            :param cy: 現在のy座標
            """
            directions = [(0, -2), (0, 2), (-2, 0), (2, 0)]
            random.shuffle(directions)
            for dx, dy in directions:
                nx, ny = cx + dx, cy + dy
                if 0 < nx < self.width - 1 and 0 < ny < self.height - 1 and self.map[ny][nx] == 1:
                    self.map[cy + dy // 2][cx + dx // 2] = 0  # 隣接マスとの間を道にする
                    self.map[ny][nx] = 0
                    carve_passages(nx, ny)

        # 初期化とスタート地点の設定
        for y in range(self.height):
            for x in range(self.width):
                self.map[y][x] = 1
        self.map[1][1] = 0  # スタート地点
        carve_passages(1, 1)
        self.place_events()

    def place_events(self) -> None:
        """
        イベントマス（回復、強化、敵、ゴール）をランダムに配置する。
        スタート地点には配置されないようにする。
        ゴールマスは迷路の端に一つだけ配置する。
        """
        # 空いているマスを取得し、スタート地点を除外
        candidates = [(x, y) for y in range(1, self.height, 2) for x in range(1, self.width, 2)
                      if self.map[y][x] == 0 and (x, y) != self.start_tile]
        edge_candidates = [(x, y) for x, y in candidates if x == 1 or y == 1 or x == self.width - 2 or y == self.height - 2]
        random.shuffle(candidates)
        random.shuffle(edge_candidates)

        # 回復マス
        if candidates:
            self.event_tiles.append((candidates.pop(), "heal"))
        # 強化マス
        for _ in range(random.randint(0, 2)):
            if candidates:
                self.event_tiles.append((candidates.pop(), "buff"))
        # 敵マス
        for _ in range(3):
            if candidates:
                self.event_tiles.append((candidates.pop(), "enemy"))
        # ゴールマス（端に一つだけ配置）
        if edge_candidates:
            goal_tile = edge_candidates.pop()
            
            self.event_tiles.append((goal_tile, "goal"))

    def draw(self, screen: pg.Surface, tile_size: int) -> None:
        """
        迷路とイベントマスを描画する。
        :param screen: Pygameの描画対象Surface
        :param tile_size: 1マスあたりのサイズ（ピクセル単位）
        """
        for y, row in enumerate(self.map):
            for x, tile in enumerate(row):
                color = (255, 255, 255) if tile == 0 else (0, 0, 0)
                pg.draw.rect(screen, color, (x * tile_size, y * tile_size, tile_size, tile_size))
        for (x, y), event in self.event_tiles:
            if event == "heal":
                color = (0, 255, 0)
            elif event == "buff":
                color = (0, 0, 255)
            elif event == "enemy":
                color = (255, 0, 0)
            elif event == "goal":
                color = (255, 255, 0)
            pg.draw.rect(screen, color, (x * tile_size, y * tile_size, tile_size, tile_size))

class Player:
    """
    プレイヤーを管理するクラス。
    """
    def __init__(self, x: int, y: int, image_path: str):
        """
        プレイヤーの初期位置と画像を設定する。
        :param x: 初期x座標
        :param y: 初期y座標
        :param image_path: プレイヤー画像のパス
        """
        self.x: int = x
        self.y: int = y
        self.image: pg.Surface = pg.image.load(image_path)
        self.moved: bool = False

    def move(self, dx: int, dy: int, game_map: list[list[int]]) -> None:
        """
        プレイヤーの移動を管理する。
        :param dx: x方向の移動量
        :param dy: y方向の移動量
        :param game_map: 現在のマップデータ
        """
        if not self.moved:
            new_x = self.x + dx
            new_y = self.y + dy
            if 0 <= new_x < len(game_map[0]) and 0 <= new_y < len(game_map):
                if game_map[new_y][new_x] == 0:  # 道のみ移動可能
                    self.x = new_x
                    self.y = new_y
            self.moved = True

    def reset_movement(self) -> None:
        """
        移動状態をリセットする。
        """
        self.moved = False

    def draw(self, screen: pg.Surface, tile_size: int) -> None:
        """
        プレイヤーを描画する。
        :param screen: Pygameの描画対象Surface
        :param tile_size: 1マスあたりのサイズ
        """
        screen.blit(self.image, (self.x * tile_size, self.y * tile_size))

def main() -> None:
    """
    ゲームのメインループ。
    """
    pg.display.set_caption("迷路ゲーム")
    screen = pg.display.set_mode((450, 450))
    clock = pg.time.Clock()
    tile_size = 50

    # プレイヤー画像の読み込み
    player_image_path = "fig/3.png"

    # マップとプレイヤーの初期化
    map_gen = MapGenerator(9, 9)
    map_gen.generate_maze()
    player = Player(1, 1, player_image_path)

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            elif event.type == pg.KEYUP:
                player.reset_movement()
        
        keys = pg.key.get_pressed()
        if keys[pg.K_UP]:
            player.move(0, -1, map_gen.map)
        if keys[pg.K_DOWN]:
            player.move(0, 1, map_gen.map)
        if keys[pg.K_LEFT]:
            player.move(-1, 0, map_gen.map)
        if keys[pg.K_RIGHT]:
            player.move(1, 0, map_gen.map)

        screen.fill((0, 0, 0))
        map_gen.draw(screen, tile_size)
        player.draw(screen, tile_size)
        pg.display.update()
        clock.tick(60)

if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
