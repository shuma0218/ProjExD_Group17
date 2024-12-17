import os
import random
import math
import sys
import pygame as pg

WIDTH = 1100  # ゲームウィンドウの幅
HEIGHT = 650  # ゲームウィンドウの高さ
os.chdir(os.path.dirname(os.path.abspath(__file__)))
NUM_ENEMYS = 3  # 敵の数
DIST_BATTLE = 5  # バトルがはじまる距離

class Player():
    """プレイヤーに関するクラス(他の人の担当分)"""
    pass
class Mapgenerator():
    """マップに関するクラス(他の人の担当分)"""
    pass

class Beam(pg.sprite.Sprite):
    """
    ビームに関するクラス
    """
    def __init__(self, chara:Player):
        """
        ビーム画像Surfaceを生成する
        引数:
        - chara: ビームを放つキャラクター
        - angle0: 回転角度（デフォルトは0）
        """
        super().__init__()
        self.x = chara.x
        self.y = chara.y
        self.vx, self.vy = chara.dire
        self.image = pg.transform.rotozoom(pg.image.load(f"fig/beam.png"), angle, 1.0)
        self.vx = math.cos(math.radians(angle))
        self.vy = -math.sin(math.radians(angle))
        self.rect = self.image.get_rect()
        self.rect.centery = chara.rect.centery + chara.rect.height * self.vy
        self.rect.centerx = chara.rect.centerx + chara.rect.width * self.vx

    def update(self):
        """
        ビームを速度ベクトルself.vx, self.vyに基づき移動させる
        """
        self.rect.move_ip(self.speed * self.vx, self.speed * self.vy)
        if check_bound(self):
            self.kill()


def distance(player:Player, enemy:Player) -> int:
    """プレイヤーと敵との距離を測る関数"""
    return abs(player.x - enemy.x) + abs(player.y-player.y)

def check_bound(chara,game_map:Mapgenerator) -> tuple[bool, bool]:
    """
    オブジェクトが画面内or画面外を判定し，真理値タプルを返す関数
    引数：こうかとんや爆弾，ビームなどのRect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    x = chara.x + chara.dx
    y = chara.x + chara.dy
    if game_map[x][y] == 0: # ビームの移動先が壁だったら
        return True
    


def main():
    pg.display.set_caption("はばたけ！こうかとん")
    screen = pg.display.set_mode((800, 600))
    init_x1, init_y1 = 1,1  # プレイヤーの初期位置
    player = Player(init_x1, init_y1)  # プレイヤーのインスタンスを生成
    enemys = pg.sprite.Group()  # 敵のインスタンスを管理するリスト
    beams_player = pg.sprite.Group()  # プレイヤーの出したビームをを管理するリスト
    beams_enemys = pg.sprite.Group()  # 敵の出したビームをを管理するリスト
    flag_battle = False  # 戦闘中かどうかを表すフラッグ
    game_over = False
    for _ in range(NUM_ENEMYS):  # 複数体の敵をグループに追加
        x,y = random.randint(random.randint(5,8),random.randint(5,8))  # 敵の座標をランダムに決める
        enemy = Player(x,y)  # 敵のインスタンスを生成
        enemys.add(enemy)
    clock  = pg.time.Clock()
    bg_img = pg.image.load("fig/pg_bg.jpg")
    tmr = 0

    while not game_over:
        for event in pg.event.get():
            if event.type == pg.QUIT: return
            if flag_battle :  # 戦闘中なら
                if event.type == pg.KEYDOWN: # キー押下時の処理
                    if event.key == pg.K_SPACE: # スペースキー押
                        beams_enemys.add(Beam(player))



        if distance(player, enemy) <= DIST_BATTLE :  # プレイヤーと敵の距離が近かったら
            flag_battle = True
        if flag_battle:  # 戦闘状態のとき
            for emy in pg.sprite.groupcollide(beams_player, enemys, True, False).keys():  #敵とビームの判定
                # プレイヤーのビームが当たった敵のリストの中身1つ1つ対して
                emy.hp -= 1 
                if enemy.hp <= 0 :  # 敵のHPが0になったら
                    # 敵が倒れるエフェクトを表示する
                    # 敵を削除する
                    pass
            for beam in pg.sprite.groupcollide(beams_enemys, player, True, False).keys():  # プレイヤーと敵のビームの判定
                # プレイヤーに当たった敵のビームに対して
                player.hp -= 1 
                if player.hp <= 0 :  # プレイヤーのHPが0になったら
                    #  こうかとんの画像を切り替える
                    game_over = True
                    return   # main関数から抜ける(ゲームオーバー)


        screen.blit(bg_img, [0, 0])
        pg.display.update()
        tmr += 1        
        clock.tick(10)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()