# はじめに

このリポジトリは、`Spring(Java)プロジェクト` をPostgreSQLのテーブルから自動生成するプロジェクトです。

# 事前準備

以下、事前準備が必要です。

1. Python3.xのインストール
2. PostgreSQLにテーブルが存在すること
    - 認証に使用するユーザテーブルが存在すること

# フォルダ構成
```
.
├── README.md
├── main.py
├── sample-psql
│   ├── docker-compose.yml
│   └── init
│       └── create_table.sql
├── setting.json
└── tmp
    ├── apiErrorMessageTmp.txt
    ├── apiResponseOptionalTmp.txt
    ├── apiResponseTmp.txt
    ├── applicationTmp.txt
    ├── bannerTmp.txt
    ├── baseControllerTmp.txt
    ├── booleanTypeTmp.txt
    ├── commonUtilsTmp.txt
    ├── constantTmp.txt
    ├── create_controllerTmp.txt
    ├── create_controllerTmp2.txt
    ├── daoTmp.txt
    ├── dateTypeTmp.txt
    ├── delete_controllerTmp.txt
    ├── editUserLockControllerTmp.txt
    ├── editUserLockRequestTmp.txt
    ├── edit_controllerTmp.txt
    ├── errorParamTmp.txt
    ├── exceptionTmp.txt
    ├── functionsTmp.txt
    ├── generatorConfigTmp.txt
    ├── get_controllerTmp.txt
    ├── get_pk_controllerTmp.txt
    ├── get_responseTmp.txt
    ├── halfAlphanumericTmp.txt
    ├── idFormatterTmp.txt
    ├── integerTypeTmp.txt
    ├── loginControllerTmp.txt
    ├── loginRequestTmp.txt
    ├── loginResponseTmp.txt
    ├── loginServiceImplTmp.txt
    ├── loginServiceTmp.txt
    ├── logoutControllerTmp.txt
    ├── longTypeTmp.txt
    ├── mapperImplTmp.txt
    ├── noDuplicateTmp.txt
    ├── numberTypeTmp.txt
    ├── pomTmp.txt
    ├── propertiesTmp.txt
    ├── requestParameterErrorResponseTmp.txt
    ├── requestParameterExceptionTmp.txt
    ├── requestTmp.txt
    ├── responseTmp.txt
    ├── resultCodeTmp.txt
    ├── securityConfigTmp.txt
    ├── serviceTmp.txt
    ├── serviceTmpImpl.txt
    ├── shortTypeTmp.txt
    └── userDetailsServiceImpl.txt
```

- `README.md`:説明ファイル。
- `main.py`:Spring(Java)プロジェクトを生成するPythonファイル。
- `sample-psql`:PostgreSQLのサンプルフォルダ。
  - `docker-compose.yml`:PostgreSQL14を起動するDocker-composeファイル。
  - `init/create_table.sql`:サンプルテーブルを作成するSQLファイル。
- `setting.json`:Spring(Java)プロジェクトの設定を行うJSONファイル。
- `tmp`:Spring(Java)プロジェクトのテンプレートを格納したフォルダ。

# 使い方

...作成中。
