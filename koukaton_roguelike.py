import os
import random
import sys
import pygame as pg

WIDTH = 1100  # ゲームウィンドウの幅
HEIGHT = 650  # ゲームウィンドウの高さ
NUM_ENEMYS = 3  # 敵の数
MAP_SIZE = 50  # 1マスのサイズ
DIST_BATTLE = 5  # バトルがはじまる距離
INIT_X, INIT_Y = 1, 1  # プレイヤーの初期位置(マップのインデックス)
os.chdir(os.path.dirname(os.path.abspath(__file__)))


class Player:
    """プレイヤーや敵に関するクラス"""
    def __init__(self, x:int, y:int, hp:int, dire:list[int,int]):
        self.x = x  #x座標に対応するリストのインデックス
        self.y = y  #y座標に対応するリストのインデックス
        self.hp = hp  # プレイヤーやキャラのHP
        self.dire = []  # x軸方向とy軸方向への移動量を表すリスト


class Mapgenerator:
    """マップに関するクラス(他の人の担当分)"""
    pass


class Beam(pg.sprite.Sprite):
    """
    プレイヤーや敵が出すビームに関するクラス
    """
    def __init__(self, chara:Player):
        """
        ビーム画像Surfaceを生成する
        引数 chara: ビームを打つキャラクター
        """
        super().__init__()
        self.x = chara.x  # ビームのx座標(マップのインデックス)
        self.y = chara.y  # ビームのy座標(マップのインデックス)
        self.dx, self.dy = chara.dire  # ビームを打ったキャラが向いている方向
        self.image = pg.transform.rotozoom(pg.image.load(f"fig/beam.png"), 0, 1.0)
        self.rect.centery = chara.rect.centery + chara.rect.height * self.dy  # 発生直後のビームの描画位置(y座標)
        self.rect.centerx = chara.rect.centerx + chara.rect.width * self.dx  # 発生直後のビームの描画位置(x座標)
        self.speed = 1

    def update(self, dire:tuple[int, int]):
        """
        ビームの座標を更新する関数
        引数 dire: ビームの移動方向を表すタプル
        戻り値：なし
        """
        xx = MAP_SIZE * (self.x + dire[0]) # リストのインデックスからスクリーンの座標に変換した値(x座標)
        yy = MAP_SIZE * (self.y + dire[1])  # リストのインデックスからスクリーンの座標に変換した値(y座標)
        self.rect.move_ip(xx, yy)  #座標の更新
        if check_collision(self):  # 壁移動先が壁だったら
            self.kill()  # ビームを削除


def distance(player:Player, enemy:Player) -> int:
    """プレイヤーと敵との距離を測る関数"""
    return abs(player.x - enemy.x) + abs(player.y-player.y)


def check_collision(chara,game_map:Mapgenerator) -> bool:
    """
    オブジェクトが画面内or画面外を判定し，真理値タプルを返す関数
    引数：プレイヤーや敵が発生させたビームのレクト
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    x = chara.x + chara.dx  # 移動先のx座標に対応するマップのインデックス
    y = chara.x + chara.dy  # 移動先のy座標に対応するマップのインデックス
    if game_map[x][y] == 0: # ビームの移動先が壁だったら
        return True
        

def main():
    pg.display.set_caption("kokaton_rouguelike")
    screen = pg.display.set_mode((800, 600))
    player = Player(INIT_X, INIT_Y)  # プレイヤーのインスタンスを生成
    enemys = pg.sprite.Group()  # 敵のインスタンスを管理するリスト
    beams_player = pg.sprite.Group()  # プレイヤーの出したビームをを管理するリスト
    beams_enemys = pg.sprite.Group()  # 敵の出したビームをを管理するリスト
    flag_battle = False  # 戦闘中かどうかを表すフラッグ
    for _ in range(NUM_ENEMYS):  # 複数体の敵をグループに追加
        x, y = random.randint(random.randint(5, 8),random.randint(5, 8))  # 敵の座標をランダムに決める
        enemy = Player(x, y)  # 敵のインスタンスを生成
        enemys.add(enemy)
    clock  = pg.time.Clock()
    bg_img = pg.image.load("fig/pg_bg.jpg")
    tmr = 0

    while True:
        if distance(player, enemy) <= DIST_BATTLE :  # プレイヤーと敵の距離が近かったら
            flag_battle = True
        for event in pg.event.get():
            if event.type == pg.QUIT: return
            if flag_battle :  # 戦闘中なら
                if event.type == pg.KEYDOWN: # キー押下時の処理
                    if event.key == pg.K_SPACE: # スペースキー押下
                        beams_player.add(Beam(player))
                        for emy in enemys:  # それぞれの敵が
                            if random.random() >= 0.08 : #一定の確立でビームを発生させる
                                beams_enemys.add(Beam(emy))

        if flag_battle:  # 戦闘状態のとき
            for emy in pg.sprite.groupcollide(beams_player, enemys, True, False).keys():  #敵とビームの判定
                # プレイヤーのビームが敵に当たるたび
                emy.hp -= 1  # 当たった敵のHPを減らす
                if enemy.hp <= 0 :  # 敵のHPが0になったら
                    emy.kill()  # 敵を削除する
            for _ in pg.sprite.groupcollide(beams_enemys, player, True, False).keys():  # プレイヤーと敵のビームの判定
                # プレイヤーに敵のビームが当たるたびに
                player.hp -= 1 
                if player.hp <= 0 :  # プレイヤーのHPが0になったら
                    return   # main関数から抜ける(ゲームオーバー)
                
        beams_player.update()  #座標の更新
        beams_player.draw() 
        beams_enemys.update()  # 座標の更新
        beams_enemys.draw()
        
        screen.blit(bg_img, [0, 0])
        pg.display.update()
        tmr += 1        
        clock.tick(10)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()