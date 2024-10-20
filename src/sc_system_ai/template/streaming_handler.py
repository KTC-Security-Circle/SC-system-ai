import logging

from queue import Queue
from langchain.callbacks.base import BaseCallbackHandler


# ロガーの設定
logger = logging.getLogger(__name__)


# StreamingHandlerクラスの作成
class StreamingAgentHandler(BaseCallbackHandler):
    def __init__(self, queue: Queue):
        super().__init__()
        self.queue = queue
    
    # トークンの生成時に呼び出される関数
    def on_llm_new_token(self, token, **kwargs):
        if token:
            logger.debug(token)
            self.queue.put(token)

    # トークン生成時にエラーが発生した場合呼び出される関数
    def on_llm_error(self, error, **kwargs):
        logger.error(f"トークンの生成時にエラーが発生しました:{error}")
        self.queue.put(None)

    def on_agent_action(self, action, **kwargs):
        pass

    # エージェントの実行終了時に呼び出される関数
    def on_agent_finish(self, response, **kwargs):
        logger.info("エージェントの実行が終了しました。")
        self.queue.put(None)


# StreamingToolHandlerクラスの作成
class StreamingToolHandler(BaseCallbackHandler):
    def __init__(self, queue: Queue):
        super().__init__()
        self.queue = queue

    def on_tool_start(self, serialized, input_str, **kwargs):
        logger.info(f"ツールの実行が開始されました。\n{serialized}\n{input_str}")

    def on_tool_finish(self, response, **kwargs):
        logger.info(f"ツールの実行が終了しました。\n{response}")

    def on_tool_error(self, error, **kwargs):
        logger.error(f"ツールの実行中にエラーが発生しました。\n{error}")


if __name__ == "__main__":
    pass
