# SCシステム AI基幹システム🤖

## 概要

このリポジトリはAI基幹システムのリポジトリになります。
GitHubからpip installできるように構築されており、再利用性を高めています。

### 使用方法

使用したいバージョンのタグを見つけ、そのタグを使用してpip install します。

```bash
# 使用したいバージョンがある場合
pip install git+https://github.com/KTC-Security-Circle/SC-system-ai.git@{使用したいバージョンのタグ}
# 最新のバージョンを使用したい場合
pip install git+https://github.com/KTC-Security-Circle/SC-system-ai.git@release
```

もし最新の開発中コードをインストールしたいときは使用したいバージョンのタグやブランチ名をなくすと最新のmainブランチのコードがインストールされます。

```bash
pip install git+https://github.com/KTC-Security-Circle/SC-system-ai.git
```

## 開発者向け

1. 自身の環境にcloneする

    - GitHubデスクトップを使用する場合

        [公式ドキュメント](https://docs.github.com/ja/desktop/adding-and-cloning-repositories/cloning-a-repository-from-github-to-github-desktop)を参考にしてcloneしてください

    - Git コマンドを使用する場合

        ```bash
        git clone git@github.com:KTC-Security-Circle/SC-system-ai.git
        ```

        もし権限がないなどのエラーが発生した場合、ssh鍵を登録する必要があるため、次のサイトを参考に登録を行う | [参考サイト](https://qiita.com/shizuma/items/2b2f873a0034839e47ce)

2. Pythonの仮想環境を構築する

    このリポジトリは以下の環境で開発することを想定しています。
    - Dockerを使用できる環境
    - Visual Studio Codeを使用できる環境

    開発環境例は以下の通りです。
    - Windows 11
    - WSL2
    - Docker Desktop
    - Visual Studio Code

    今回は3.10系で開発するため、`.devcontainer/devcontainer.json`と`pyproject.toml`にバージョンを指定しています。
    もしバージョンを持っていない場合は別途インストールしてください。

    Devcontainerを起動します。

    ```bash
    cd SC-system-ai
    code .
    ```

    VS Codeが開いたら、左下の緑色のアイコンをクリックして"Reopen in Container"を選択します。

    正しく環境が構築されると、`poetry install`が実行され、.venvとrequirements.txtが生成されます。
    自動的にインタプリタが設定されるはずなので、そのまま開発ができるようになっています。
    > **※** 初めてDevcontainerを起動するときは、Dockerイメージのビルドが行われるため、時間がかかることがあります。
    git コマンドに関して使用できるようにしていますが、ssh鍵の設定が必要な場合があります。
    推奨事項としてはコンテナ外からgitコマンドを使用することをお勧めします.

3. 環境変数を設定する

   `.env.sample`ファイルをコピーし、[docs/env.md](docs/env.md)で確認しながら設定を行う

4. 開発を始める

   [開発者向けドキュメント](docs/developer.md)から始めてください。
