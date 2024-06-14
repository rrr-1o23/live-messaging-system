# Live Messaging System

#### 使用技術
<p style="display: inline">
<img src="https://img.shields.io/badge/-Linux-212121.svg?logo=linux&style=popout">
<img src="https://img.shields.io/badge/-Python-FFC107.svg?logo=python&style=popout">
</p>

&nbsp;

## 概要

Live Messaging Systemを開発しました．クライアントがサーバのリソースを利用してチャットルームの作成・参加ができる分散型システムです．プロセス間通信にはソケットプログラミングを採用し，重要な操作にはTCPソケット，リアルタイム性が重視される操作にはUDPソケットを採用しています．

#### 操作方法
1. ターミナルからserver.pyを立ち上げる<br>
```bash
$ python server.py
```

2. 別のターミナルを立ち上げclient.pyを立ち上げる<br>
```bash
$ python client.py
connecting to 0.0.0.0
接続できました.

ユーザー名を入力してください → User1 

1または2を入力してください (1: ルーム作成, 2: ルームに参加) → 1
チャット開始
```
3. client.pyをさらに別のターミナルを立ち上げルームに参加すれば，クライアント同士でチャット可能

&nbsp;

## 環境
| OS・言語・ライブラリ | バージョン |
| :------- | :------ |
| Ubuntu | 22.04.4 LTS |
| Python | 3.10.12 |

&nbsp;