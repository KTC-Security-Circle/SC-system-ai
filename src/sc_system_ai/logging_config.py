"""
### loggingの設定を行うモジュール

使用例:
```python
import logging

logger = logging.getLogger(__name__)

logger.info("ログメッセージ")
logger.debug("デバッグ時のみ使用するログメッセージ")

# デバッグ時のみログメッセージを出力するためには、以下のように設定する
if __name__ == "__main__":
    from sc_system_ai.logging_config import setup_logging
    setup_logging()
```
"""
import logging

from langchain.globals import set_verbose


def setup_logging() -> None:
    # ロギングの設定
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()  # コンソールにログメッセージを出力
        ]
    )

    # 自作パッケージのロガーを設定
    # この設定を行うことで、自作パッケージのログメッセージのみDEBUGレベルで出力される
    # sc_system_ai以下のモジュールでloggerを取得する場合と__main__でloggerを取得する場合でログレベルを変更する
    package_logger = logging.getLogger("__main__")
    package_logger.setLevel(logging.DEBUG)
    package_logger = logging.getLogger("sc_system_ai")
    package_logger.setLevel(logging.DEBUG)

    # langchainのログメッセージを出力する
    set_verbose(True)
