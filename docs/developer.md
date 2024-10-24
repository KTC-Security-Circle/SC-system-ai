# 開発者向けドキュメント

## 目次
- [開発者向けドキュメント](#開発者向けドキュメント)
  - [目次](#目次)
  - [環境のセットアップ](#環境のセットアップ)
  - [開発に参加する](#開発に参加する)
    - [コーディングを始める前に](#コーディングを始める前に)
    - [コーディングスタイルガイドライン](#コーディングスタイルガイドライン)
    - [テストの実行](#テストの実行)
    - [ブランチ戦略](#ブランチ戦略)
    - [プルリクエストの作成](#プルリクエストの作成)
    - [コードレビュー](#コードレビュー)
  - [FAQ](#faq)
    - [よくある質問](#よくある質問)
    - [サポート](#サポート)


## 環境のセットアップ

ソースコードを実行するためには、必要な環境をセットアップする必要があります。
プロジェクトのREADMEに始め方を書いているので、そちらを参考に進めてください。


## 開発に参加する

まずは環境構築を行った後に[studies/chain.py](../studies/chain.py)を実行し、エラーなく実行できるところまで確認してください。
これが第一歩となります。

### コーディングを始める前に

コーディングを始める前に `git pull` を打つ癖をつけましょう。
コンフリクトを未然に防ぎ、ほかのメンバーと共同開発しやすくなります。
作業のコミットは定期的に行いましょう。
あとから履歴をさかのぼる際に楽になります。

### コーディングスタイルガイドライン

- コードはPEP8に準拠してください。 [PEP8について](https://peps.python.org/pep-0008/)
  ただし、あくまでガイドラインなので厳密に従う必要はありません。


### テストの実行

現在まだテストコードは作成していません。
ある程度開発した段階で作成予定をしていますが、現在はそれぞれのファイル内で次のような形でデバッグしてください。

```python
# デバッグしたいファイルの最下部に
if __name__ == __main__:
    # ここにデバッグしたいコードを記述
```

作成するモジュールの重要個所ではloggingをしてください。

```python
import logging


logger = logging.getLogger(__name__)
```

上記で設定した後、次のように表示させる

```python
logger.info("ログメッセージ")
logger.debug("デバッグ時のみ使用するログメッセージ")

# デバッグ時のみログメッセージを出力するためには、以下のように設定する
if __name__ == __main__:
    from sc_system_ai.logging_config import setup_logging
    setup_logging()
```

### ブランチ戦略

- 新しい機能やバグ修正は必ずブランチを切って作業してください。ブランチ名は以下の命名規則に従ってください。
    - 機能追加: `feature/機能名`
    - バグ修正: `fix/バグ名`
    - ドキュメント追加・修正: `docs/追加・修正するドキュメント名`

### プルリクエストの作成

- 作業が完了したら、プルリクエストを作成してください。プルリクエストには、どういった変更を行ったのかをできるだけ具体的に書いてください

### コードレビュー

- プルリクエストは、他の開発者によるコードレビューを経てマージされます。レビューの際には、以下の点に注意してください。
    - コードが意図した通りに動作することを確認する
    - コーディングスタイルに準拠していることを確認する
    - 適切なテストが作成されていることを確認する

## FAQ

### よくある質問

- **依存関係のインストール中にエラーが発生しました**
    - Pythonのバージョンやpipのバージョンを確認し、必要に応じてアップデートしてください。
    - 仮想環境が正しくアクティベートされていることを確認してください。

- **テストが失敗します**
    - テストのログを確認し、問題の箇所を特定してください。
    - 依存関係が最新のものであることを確認し、必要に応じて再インストールしてください。

### サポート

- その他の質問やサポートが必要な場合は、プロジェクトのSlackチャンネルまたはメールでお問い合わせください。