"""
### loggingの設定を行うモジュール

使用例:
```python
import logging
from sc_system_ai.logging_config import setup_logging

logger = logging.getLogger(__name__)

logger.info("ログメッセージ")
logger.debug("デバッグ時のみ使用するログメッセージ")
```
"""
import logging


def setup_logging():
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
    package_logger = logging.getLogger("sc_system_ai")
    package_logger.setLevel(logging.DEBUG)
    debug_logger = logging.getLogger("__main__")
    debug_logger.setLevel(logging.DEBUG)

