"""
### Agentの基底クラス

Agentの基底クラスを作成します。このクラスは、エージェントの情報を保持し、エージェントを実行するための関数を提供します。

詳しい使用方法は `docs/make-agent.md` を参照してください。

"""
import logging
from queue import Queue
from threading import Thread
from typing import Type

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

        self.is_streaming = is_streaming

        # assistant_infoとtoolsは各エージェントで設定する
        self.assistant_info = None
        self.tools = []
        self.set_tools(template_tools)

        # ストリーミングの設定
        if self.is_streaming:
            self.queue = Queue()
            self.handler = StreamingAgentHandler(self.queue)
            self._streaming_agent_setup()
            self.return_length = return_length

        self._create_invoke()


        self.prompt_template = PromptTemplate(assistant_info=self.assistant_info, user_info=self.user_info)

        self.get_agent_info()
    
    def set_tools(self, tools: list[Type[BaseTool]]):
        """ツールを追加する関数"""
        self.tools += self._streaming_tool_setup(tools) if self.is_streaming else tools

    def set_assistant_info(self, assistant_info: str):
        """アシスタント情報を設定する関数"""
        self.assistant_info = assistant_info
        self.prompt_template.create_prompt(assistant_info=self.assistant_info)
    
    def _streaming_agent_setup(self) -> None:
        """エージェントのストリーミングのセットアップを行う関数"""
        self.llm.streaming = True
        self.llm.callbacks = [self.handler]

    def _streaming_tool_setup(self, tools: list[Type[BaseTool]]) -> list[Type[BaseTool]]:
        """ツールのストリーミングのセットアップを行う関数"""
        handler = StreamingToolHandler(self.queue)
        for tool in tools:
            tool.callbacks = [handler]

        return tools
    
    def invoke(self, message: str):
        """
        エージェントを実行する関数

        Args:
            message (str): ユーザーからのメッセージ

        is_streamingがTrueの場合は、ジェネレータとなります
        ```python
        for output in agent.invoke("user message"):
            print(output)
        ```
        """
        pass

    def _create_invoke(self) -> None:
        if self.is_streaming:
            def invoke(self, message: str):
                yield from self._streaming_invoke(message)
        else:
            def invoke(self, message: str):
                self._invoke(message)
                return self.result
        setattr(self.__class__, "invoke", invoke)

    def _setup_invoke(self):
        agent = create_tool_calling_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt_template.full_prompt
        )
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            callbacks= [self.handler] if self.is_streaming else None
        )
        self.result = ""
    
    def _invoke(self, message: str):
        self._setup_invoke()
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
        self._setup_invoke()
        phrase = ""
        thread = Thread(target=self._invoke, args=(message,))

        thread.start()
        try:
            while True:
                token = self.handler.queue.get()
                if token is None:
                    break

                phrase += token
                if len(phrase) >= self.return_length:
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
            tools=self.tools
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
        llm=llm
    )
    agent.assistant_info = "あなたは優秀な校正者です。"
    agent.set_tools(tools)
    
    # result = agent.invoke("magic function に３")
    # print(result)

    for output in agent.invoke("magic function に３"):
        print(output)
    print(agent.get_response())
