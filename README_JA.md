# HomuraMC [![Discord](https://img.shields.io/discord/1141329766889300070.svg?label=&logo=discord&logoColor=ffffff&color=7389D8&labelColor=6A7EC2)](https://discord.gg/967gvTTEWc)

[English](README.md) | 日本語

HomuraMCは、Pythonで書かれたオープンソースMinecraftサーバーソフトウェアです。

[私たちのDiscordに参加してください](https://discord.gg/967gvTTEWc)
## 使い方（サーバー管理者）
> [!WARNING]  
> Homuraは、ほとんどの機能がまだ実装されていないα版です！本番環境で使用することはお勧めしません！
### 要件
* Python3
* Git (Releaseから取得しない場合)
### 手順
(リポジトリをクローンして取得する場合)

まず、次のコマンドを実行して、このリポジトリをクローンします。
```
git clone https://github.com/HomuraMC/Homura.git
```
取得したら、Python仮想環境を作成します（推奨）
```
# Windows
python -m venv homura

# Other
python3 -m venv homura
```
仮想環境を作成した場合は、次のコマンドを使用して仮想環境にPythonにアクセスしてください。
```
# Windows
./homura/scripts/Activate

# Other
source homura/bin/activate
```
次に、pipを使用して、Homuraが必要とするライブラリをインストールします。
```
# Windows
pip install -r requirements.txt
# Other
python3 -m pip install -r requirements.txt
```
インストール後、次のコマンドを実行してサーバーを開始できます。
```
python3 main.py
```

## トラブルシューティング
### 私の友人はサーバーに接続できません
Homura.iniファイルでポート（デフォルトは25565）、およびルーターでHomura.iniに記載されているポートが開いていることを確認します。ポートを開くことができない場合は、[playit（https://playit.gg）](https://playit.gg/)を使用して公開することができます。

### ここで言及されていないものについて助けが必要です
[ここ](https://github.com/HomuraMC/Homura/issues)で問題を開くか[Discord](https://discord.gg/967gvTTEWc)で助けを求めることができます。

## スクリーンショット
いつか貼ります

## 特別な感謝
- [https://qiita.com/YuzuRyo61/items/da7a6e55616254eb63d7](https://qiita.com/YuzuRyo61/items/da7a6e55616254eb63d7)
- [https://github.com/barneygale/quarry/issues/135#issuecomment-1088143509](https://github.com/barneygale/quarry/issues/135#issuecomment-1088143509)
- [https://github.com/TMShader/QuarryMinecraftServerTests/](https://github.com/TMShader/QuarryMinecraftServerTests/)
