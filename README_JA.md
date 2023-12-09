# HomuraMC [![Discord](https://img.shields.io/discord/1141329766889300070.svg?label=&logo=discord&logoColor=ffffff&color=7389D8&labelColor=6A7EC2)](https://discord.gg/967gvTTEWc)

[English](https://github.com/HomuraMC/Homura/blob/main/README.md) | 日本語

HomuraMCは、Pythonで書かれたオープンソースMinecraftサーバーソフトウェアです。

[私たちのDiscordに参加してください](https://discord.gg/967gvTTEWc)
## 使い方（サーバー管理者）
> [!WARNING]  
> Homuraは、ほとんどの機能がまだ実装されていないα版です！本番環境で使用することはお勧めしません！
### 要件
* Python3
* Java16 (Homuraはチャンクの生成にバニラjarを利用します)
* Git (Releaseから取得しない場合)
### 手順
(リポジトリをクローンして取得する場合)

まず、次のコマンドを実行して、このリポジトリをクローンします。
```
git clone https://github.com/HomuraMC/Homura.git
```
取得したら、Python仮想環境を作成します（推奨）
```
python -m venv homura
```
仮想環境を作成した場合は、次のコマンドを使用して仮想環境にPythonにアクセスしてください。
```
./homura/scripts/Activate
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
### [WinError 2] 指定されたファイルが見つかりません と表示される
Java（JDK）は、世界の生成にバニラjarを使用する必要があります。そのため、Java16が必要です。
[java16はここから取得できます。 ( https://www.oracle.com/java/technologies/downloads/ )](https://www.oracle.com/java/technologies/downloads/)

### 私の友人はサーバーに接続できません
Homura.iniファイルでポート（デフォルトは25565）、およびルーターでHomura.iniに記載されているポートが開いていることを確認します。ポートを開くことができない場合は、[playit（https://playit.gg）](https://playit.gg/)を使用して公開することができます。

### ここで言及されていないものについて助けが必要です
[ここ](https://github.com/HomuraMC/Homura/issues)で問題を開くか[Discord](https://discord.gg/967gvTTEWc)で助けを求めることができます。

## スクリーンショット
![Chunk send test](https://cdn.discordapp.com/attachments/1141329767858196522/1163013839932112987/image.png?ex=653e080b&is=652b930b&hm=7dcf4c7fb4ccfb8c7143032305758ab179d690f00d7ee3ac2684f9cfdefa9476&)  
![plugin test](https://cdn.discordapp.com/attachments/1141329767858196522/1162564910253879416/image.png?ex=653c65f2&is=6529f0f2&hm=d92e2095fad488ea43bb54c094ea6edfc968a84b865283ed6d1b3d85821c6ee9&)
![plugin test 2](https://cdn.discordapp.com/attachments/1141329767858196522/1162565031901282324/image.png?ex=653c660f&is=6529f10f&hm=48022d707ae097bc4c75a2df44efb9cf0be58272471aec67d92002d34cb65cf6&)

## 特別な感謝
- [https://qiita.com/YuzuRyo61/items/da7a6e55616254eb63d7](https://qiita.com/YuzuRyo61/items/da7a6e55616254eb63d7)
- [https://github.com/barneygale/quarry/issues/135#issuecomment-1088143509](https://github.com/barneygale/quarry/issues/135#issuecomment-1088143509)
- [https://github.com/TMShader/QuarryMinecraftServerTests/](https://github.com/TMShader/QuarryMinecraftServerTests/)