# SCシステム AI基幹システム

## 概要

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
    
    今回は3.10系で開発するため、バージョンを指定している

    もしバージョンを持っていない場合は別途インストールしてください

    ```bash
    py -3.10 -m venv .venv
    ```

    仮想環境にpip install する

    ```bash
    .\.venv\Scripts\activate
    pip install -r requirements.txt
    ```

3. 環境変数を設定する
   
   `.env.sample`ファイルをコピーし、[docs/env.md](docs/env.md)で確認しながら設定を行う
