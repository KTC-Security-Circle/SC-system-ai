"""
### loggingの設定を行うモジュール

使用例:
```python
import logging
from sc_system_ai.logging_config import setup_logging

logger = logging.getLogger(__name__)
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
    package_logger = logging.getLogger('sc_system_ai')
    package_logger.setLevel(logging.DEBUG)

setup_logging()