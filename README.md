# ローグライクこうかとん

## 実行環境の必要条件
* python >= 3.10
* pygame >= 2.1

## ゲームの概要
* 主人公キャラクターこうかとんが探索するゲーム
* 9×9の迷路上のマップを自動生成しローグライク要素を追加
* 敵マスにプレイヤーが到達するとターン制の戦闘が開始
* マップを作成し一つのマップをクリヤすると次のマップへ
* マップ内にはプレイヤーのスキルを強化したり、新しいスキルを選択できる強化マス、プレイヤーhpを回復できる回復マス、敵が存在する敵マスを用意
* プレイヤーは最大でスキルを4つまで持てる
* マップを進むにつれて敵ガ強化される
* 参考URL：[サイトタイトル](https://www.hoge.com/)

## ゲームの遊び方
* プレイヤーは十字キーでマップ内を移動
* 戦闘シーンではプレイヤーがスキルを選び行動する

## ゲームの実装
### 共通基本機能
* 背景画像と主人公キャラクターの描画

### 分担追加機能
* マップ自動生成（担当：ふしみ）：9×9の迷路となっているマップの自動生成
* 戦闘シーン（担当：ぷしみ）：プレイヤーと敵のターン制の戦闘
* bgm実装（担当：ぶしみ）：探索フェイズや戦闘時のbgm実装
* キャラクター強化 (担当 : 酒井)　: プレイヤーの強化に関する関数
### ToDo
- [ ] ほげほげ機能
- [ ] ふがふが関数内の変数名の統一

### メモ
* クラス内の変数は，すべて，「get_変数名」という名前のメソッドを介してアクセスするように設計してある
* すべてのクラスに関係する関数は，クラスの外で定義してある
