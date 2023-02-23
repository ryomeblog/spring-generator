# 前提条件

1. Docker-composeを実行できる環境
    - [UbuntuにDockerをインストールする手順](https://qiita.com/ryome/items/4b6b934b1b2021acfa26)
    - [UbuntuにDocker-composeをインストールする手順](https://qiita.com/ryome/items/56a3263f347a08bd860f)

# フォルダ構造
```
.
├── app
│   ├── Dockerfile
│   ├── main.py
│   ├── requirements.txt
│   ├── setting.json
│   └── tmp
├── docker-compose.yml
├── init
│   └── create_table.sql
└── readme.md
```

# 使い方

1. 資材をローカルにダウンロードします。
- コマンド
```
git clone https://github.com/ryomeblog/spring-generator.git
cd spring-generator/sample-generator
```
- 実行例
```
$ git clone https://github.com/ryomeblog/spring-generator.git
Cloning into 'spring-generator'...
remote: Enumerating objects: 70, done.
remote: Counting objects: 100% (70/70), done.
remote: Compressing objects: 100% (55/55), done.
remote: Total 70 (delta 18), reused 66 (delta 14), pack-reused 0
Unpacking objects: 100% (70/70), 34.83 KiB | 1.39 MiB/s, done.
$ cd spring-generator/sample-generator
```

2. Docker-Composeを起動させます。
- コマンド
```
docker-compose up -d
```
- 実行例
```
$ docker-compose up -d --build
Building app
Sending build context to Docker daemon    193kB
...省略
Creating test-postgres ... done
Creating test-spring-generator ... done
```

3. コンテナ内でmain.pyを実行します
- コマンド
```
docker-compose exec app python main.py
```
- 実行例
```
$ docker-compose exec app python main.py
```

4. 実行結果を確認します。

`./app` 配下に `log` フォルダ と `generator` フォルダが作成されていれば成功です。

- コマンド
```
ls app
```
- 実行例
```
$ ls app
Dockerfile  generator  generator.json  log  main.py  requirements.txt  setting.json  tmp
```