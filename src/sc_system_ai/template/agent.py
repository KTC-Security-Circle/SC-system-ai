"""
### Agentの基底クラス

Agentの基底クラスを作成します。このクラスは、エージェントの情報を保持し、エージェントを実行するための関数を提供します。

詳しい使用方法は `docs/make-agent.md` を参照してください。

"""
import logging
from queue import Queue
from threading import Thread
from typing import Type, Iterator

from langchain_openai import AzureChatOpenAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.tools import BaseTool

from sc_system_ai.template.ai_settings import llm
from sc_system_ai.template.user_prompts import User
from sc_system_ai.template.system_prompt import PromptTemplate
from sc_system_ai.agents.tools import magic_function, search_duckduckgo
from sc_system_ai.template.streaming_handler import (
    StreamingAgentHandler,
    StreamingToolHandler
)

# ロガーの設定
logger = logging.getLogger(__name__)

# ToolManagerクラスの作成
class ToolManager:
    """
    ツールを管理するクラス

    Args:
        tools (list[Type[BaseTool]], optional): ツールのリスト. Defaults to [].
        is_streaming (bool, optional): ストリーミングの有無. Defaults to True.
        queue (Queue, optional): キュー. Defaults to None.
    """
    def __init__(
            self,
            tools: list[Type[BaseTool]] = [],
            is_streaming: bool = True,
            queue: Queue = None,
    ):
        self.tools = tools
        self._is_streaming = is_streaming
        self.queue = queue

    @property
    def is_streaming(self):
        return self._is_streaming
    
    @is_streaming.setter
    def is_streaming(self, is_streaming: bool):
        self._is_streaming = is_streaming

        if self._is_streaming:
            self.tools = self.setup_streaming(self.tools)
        else:
            self.cancel_streaming()

    def setup_streaming(self, tools: list[Type[BaseTool]]) -> list[Type[BaseTool]]:
        """ストリーミングのセットアップを行う関数"""
        self.handler = StreamingToolHandler(self.queue)

        for tool in tools:
            tool.callbacks = [self.handler]

        return tools

    def cancel_streaming(self):
        """ストリーミングのセットアップを解除する関数"""
        for tool in self.tools:
            tool.callbacks = None

    def set_tools(self, tools: list[Type[BaseTool]]):
        """ツールを追加する関数"""
        self.tools += self.setup_streaming(tools) if self._is_streaming else tools



# 全てのAgentに共通するツール
template_tools = [search_duckduckgo]

# エージェント情報のテンプレート
agent_info = """
エージェント情報:
-------------------
    assistant_info: {assistant_info}
    user_info: {user_info}
    tools: {tools}
-------------------
"""

# Agentクラスの作成
class Agent:
    """
    Agentクラス

    Args:
        llm (AzureChatOpenAI, optional): OpenAIのモデル. Defaults to llm.
        user_info (User, optional): ユーザー情報. Defaults to User().
        is_streaming (bool, optional): ストリーミングの有無. Defaults to True.
        return_length (int, optional): ストリーミング時の返答の長さ. Defaults to 5.
    """
    def __init__(
            self,
            llm: AzureChatOpenAI = llm,
            user_info: User = User(),
            is_streaming: bool = True,
            return_length: int = 5
    ):
        self.llm = llm
        self.user_info = user_info

        self._is_streaming = is_streaming
        self._return_length = return_length
        self.queue = Queue()
        
        # assistant_infoとtoolsは各エージェントで設定する
        self.assistant_info = None
        self.tool = ToolManager(tools=template_tools, is_streaming=self._is_streaming, queue=self.queue)

        self.prompt_template = PromptTemplate(assistant_info=self.assistant_info, user_info=self.user_info)

        if self._is_streaming:
            self.setup_streaming()

        self.get_agent_info()

    @property
    def is_streaming(self):
        return self._is_streaming
    
    @is_streaming.setter
    def is_streaming(self, is_streaming: bool):
        self._is_streaming = is_streaming
        self.tool.is_streaming = is_streaming

        if self._is_streaming:
            self.setup_streaming()
        else:
            self.cancel_streaming()

    @property
    def return_length(self):
        return self._return_length

    @return_length.setter
    def return_length(self, return_length: int):
        if return_length <= 0:
            raise ValueError("return_lengthは1以上の整数である必要があります。")
        self._return_length = return_length

    def setup_streaming(self):
        """ストリーミング時のセットアップを行う関数"""
        self.clear_queue()
        self.handler = StreamingAgentHandler(self.queue)

        # llmの設定
        self.llm.streaming = True
        self.llm.callbacks = [self.handler]

    def cancel_streaming(self):
        """ストリーミング時のセットアップを解除する関数"""
        self.llm.streaming = False
        self.llm.callbacks = None

    def clear_queue(self):
        """キューをクリアする関数"""
        while not self.queue.empty():
            self.queue.get()

    def set_assistant_info(self, assistant_info: str):
        """アシスタント情報を設定する関数"""
        self.assistant_info = assistant_info
        self.prompt_template.create_prompt(assistant_info=self.assistant_info)

    def set_tools(self, tools: list[Type[BaseTool]]):
        """ツールを設定する関数"""
        self.tool.set_tools(tools)
    
    def invoke(self, message: str) -> Iterator[str]:
        """
        エージェントを実行する関数

        Args:
            message (str): ユーザーからのメッセージ

        is_streamingがTrueの場合、エージェントからストリーミングでレスポンスを取得し、返却します。
        ```python
        for output in agent.invoke("user message"):
            print(output)
        ```

        is_streamingがFalseの場合は、エージェントのレスポンスを取得後、返却します
        ```python
        resp = next(agent.invoke("user message"))
        ```
        """
        agent = create_tool_calling_agent(
            llm=self.llm,
            tools=self.tool.tools,
            prompt=self.prompt_template.full_prompt
        )
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tool.tools,
            callbacks= [self.handler] if self._is_streaming else None
        )
        self.result = ""

        if self._is_streaming:
            yield from self._streaming_invoke(message)
        else:
            self._invoke(message)
            yield self.result
    
    def _invoke(self, message: str):
        try: # エージェントの実行
            logger.info("エージェントの実行を開始します。\n-------------------\n")
            logger.debug(f"最終的なプロンプト: {self.prompt_template.full_prompt.messages}")
            self.result = self.agent_executor.invoke({
                "chat_history": self.user_info.conversations.format_conversation(),
                "messages": message, 
            })
        except Exception as e:
            logger.error(f"エージェントの実行に失敗しました。エラー内容: {e}")
            self.result = "エージェントの実行に失敗しました。"
    
    def _streaming_invoke(self, message: str):
        phrase = ""
        thread = Thread(target=self._invoke, args=(message,))

        thread.start()
        try:
            while True:
                token = self.handler.queue.get()
                if token is None:
                    break

                phrase += token
                if len(phrase) >= self._return_length:
                    yield phrase
                    phrase = ""
        except Exception as e:
            logger.error(f"エラーが発生しました:{e}")
        finally:
            yield phrase

            #クリーンアップ
            if thread and thread.is_alive():
                thread.join()

    def get_response(self):
        """エージェントのレスポンスを取得する関数"""
        try:
            resp = self.result
        except AttributeError:
            return "エージェントの実行が行われていません。"
        else:
            return resp
    
    def get_agent_info(self):
        """Agentの情報を取得する関数"""
        self.agent_info = agent_info.format(
            assistant_info=self.assistant_info,
            user_info=self.user_info,
            tools=self.tool.tools
        )
        return self.agent_info
    
    def display_agent_info(self):
        """Agentの情報を表示する関数"""
        self.get_agent_info()
        print(self.agent_info)
    
    def get_agent_prompt(self):
        """Agentのプロンプトを取得する関数"""
        return self.prompt_template.get_prompt()
    
    def display_agent_prompt(self):
        """Agentのプロンプトを表示する関数"""
        self.prompt_template.display_prompt()



if __name__ == "__main__":
    from sc_system_ai.logging_config import setup_logging
    setup_logging()
    # ユーザー情報
    user_name = "hogehoge"
    user_major = "fugafuga専攻"
    history = [
        ("human", "こんにちは!"),
        ("ai", "本日はどのようなご用件でしょうか？")
    ]
    user_info = User(name=user_name, major=user_major)
    user_info.conversations.add_conversations_list(history)

    tools = [magic_function]
    agent = Agent(
        user_info=user_info,
        llm=llm,
        is_streaming=False
    )
    agent.assistant_info = "あなたは優秀な校正者です。"
    agent.tool.set_tools(tools)
    
    result = next(agent.invoke("magic function に３"))
    print(result)

    agent.is_streaming = True
    for output in agent.invoke("magic function に３"):
        print(output)
    print(agent.get_response())
