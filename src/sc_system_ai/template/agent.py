"""
### Agentの基底クラス

Agentの基底クラスを作成します。このクラスは、エージェントの情報を保持し、エージェントを実行するための関数を提供します。

詳しい使用方法は `docs/make-agent.md` を参照してください。

"""
import logging
from collections.abc import AsyncIterator
from queue import Queue
from threading import Thread
from typing import Any, Literal

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.tools import BaseTool
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import AzureChatOpenAI
from pydantic import BaseModel, ConfigDict

from sc_system_ai.agents.tools import magic_function, search_duckduckgo
from sc_system_ai.template.ai_settings import llm
from sc_system_ai.template.streaming_handler import StreamingAgentHandler, StreamingToolHandler
from sc_system_ai.template.system_prompt import PromptTemplate
from sc_system_ai.template.user_prompts import User

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
            queue: Queue,
            tools: list | None = None,
    ):
        self.tools: list[BaseTool] = []
        self.queue = queue
        self.handler = StreamingToolHandler(self.queue)
        if tools is not None:
            self.set_tools(tools)

    def setup_streaming(self) -> None:
        """ストリーミングのセットアップを行う関数"""
        for tool in self.tools:
            tool.callbacks = [self.handler]

    def cancel_streaming(self) -> None:
        """ストリーミングのセットアップを解除する関数"""
        for tool in self.tools:
            tool.callbacks = None

    def set_tools(self, tools: list) -> None:
        """ツールを追加する関数"""
        if not all(self._tool_checker(tool) for tool in tools):
            raise ValueError("ツールの追加に失敗しました。")
        for tool in tools:
            if self._tool_checker(tool):
                self.tools.append(tool)
            else:
                raise ValueError("ツールの追加に失敗しました。")

    def _tool_checker(self, tool: Any) -> bool:
        """ツールのチェックを行う関数"""
        result = False
        if isinstance(tool, DuckDuckGoSearchRun):
            result = True
        elif isinstance(tool, BaseTool):
            result = True
        return result



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
# Agentのレスポンスの型
class BaseAgentResponse(BaseModel):
    """Agentのレスポンスの型"""
    output: str | None = None
    error: str | None = None

    model_config = ConfigDict(
        validate_assignment=True
    )

class AgentResponse(BaseAgentResponse):
    """Agentのレスポンスの型"""
    chat_history: list[HumanMessage | AIMessage] | None = None
    messages: str | None = None
    document_id: list[int] | None = None


class StreamingAgentResponse(BaseAgentResponse):
    """Agentのストリーミングレスポンスの型"""
    status: Literal["processing", "completed", "error"] | None = None

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
            user_info: User | None = None,
    ):
        self.llm = llm
        self.user_info = user_info if user_info is not None else User()

        self.result: AgentResponse
        self.queue: Queue = Queue()
        self.handler = StreamingAgentHandler(self.queue)

        # assistant_infoとtoolsは各エージェントで設定する
        self.assistant_info = ""
        self.tool = ToolManager(tools=template_tools, queue=self.queue)

        self.prompt_template = PromptTemplate(assistant_info=self.assistant_info, user_info=self.user_info)

        self.get_agent_info()

    def setup_streaming(self) -> None:
        """ストリーミング時のセットアップを行う関数"""
        self.clear_queue()
        self.llm.streaming = True
        self.llm.callbacks = [self.handler]
        self.tool.setup_streaming()

    def cancel_streaming(self) -> None:
        """ストリーミング時のセットアップを解除する関数"""
        self.llm.streaming = False
        self.llm.callbacks = None
        self.tool.cancel_streaming()

    def clear_queue(self) -> None:
        """キューをクリアする関数"""
        while not self.queue.empty():
            self.queue.get()

    def set_assistant_info(self, assistant_info: str) -> None:
        """アシスタント情報を設定する関数"""
        self.assistant_info = assistant_info
        self.prompt_template.create_prompt(assistant_info=self.assistant_info)

    def set_tools(self, tools: list) -> None:
        """ツールを設定する関数"""
        self.tool.set_tools(tools)

    def invoke(self, message: str) -> AgentResponse:
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
        self.cancel_streaming()
        self._invoke(message, False)
        return self.get_response()

    async def stream(
        self,
        message: str,
        return_length: int = 5
    ) -> AsyncIterator[StreamingAgentResponse]:
        """
        エージェントをストリーミングで実行する関数

        Args:
            message (str): ユーザーからのメッセージ

        ```python
        for output in agent.stream("user message"):
            print(output)
        ```
        """
        self.setup_streaming()
        phrase = ""
        thread = Thread(target=self._invoke, args=(message, True,))
        thread.start()
        try:
            while True:
                if self.queue.empty():
                    continue

                token = self.handler.queue.get()
                if token is None:
                    logger.debug("エージェントの実行が終了しました。")
                    break
                phrase += token
                if len(phrase) >= return_length:
                    yield StreamingAgentResponse(
                        output=phrase, error=None, status="processing"
                    )
                    phrase = ""
        except Exception as e:
            logger.error(f"エラーが発生しました:{e}")
            yield StreamingAgentResponse(
                output=None, error=f"エラーが発生しました:{e}", status="error"
            )

        if thread and thread.is_alive():
            thread.join()
        yield StreamingAgentResponse(output=phrase, error=None, status="completed")

    def _invoke(self, message: str, streaming: bool) -> None:
        agent = create_tool_calling_agent(
            llm=self.llm,
            tools=self.tool.tools,
            prompt=self.prompt_template.full_prompt
        )
        agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tool.tools,
            callbacks= [self.handler] if streaming else None
        )
        try: # エージェントの実行
            logger.info("エージェントの実行を開始します。\n-------------------\n")
            logger.debug(f"最終的なプロンプト: {self.prompt_template.full_prompt.messages}")
            resp = agent_executor.invoke({
                "chat_history": self.user_info.conversations.format_conversation(),
                "messages": message,
            })

            if "output" in resp:
                self.result = AgentResponse(
                    chat_history=resp.get("chat_history"),
                    messages=resp.get("messages"),
                    output=resp.get("output"),
                )
            else:
                logger.error("エージェントの実行結果取得に失敗しました。")
                logger.debug(f"エージェントの実行結果: {resp}")
                raise RuntimeError("エージェントの実行結果取得に失敗しました。")
        except Exception as e:
            logger.error(f"エージェントの実行に失敗しました。エラー内容: {e}")
            self.result = AgentResponse(error=f"エージェントの実行に失敗しました。エラー内容: {e}")

    async def stream_on_tool(self, message: str) -> None:
        """ツール上でストリーミングでエージェントを実行する関数"""
        self.handler.queue = self.queue
        self.setup_streaming()
        agent = create_tool_calling_agent(
            llm=self.llm,
            tools=self.tool.tools,
            prompt=self.prompt_template.full_prompt
        )
        agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tool.tools,
            callbacks= [self.handler],
        )
        resp = await agent_executor.ainvoke({
            "chat_history": self.user_info.conversations.format_conversation(),
            "messages": message,
        })
        self.result = AgentResponse(
            chat_history=resp.get("chat_history"),
            messages=resp.get("messages"),
            output=resp.get("output"),
        )


    def get_response(self) -> AgentResponse:
        """エージェントのレスポンスを取得する関数"""
        try:
            resp = self.result
        except AttributeError:
            return AgentResponse(error="エージェントの実行結果がありません。")
        else:
            return resp

    def get_agent_info(self) -> str:
        """Agentの情報を取得する関数"""
        self.agent_info = agent_info.format(
            assistant_info=self.assistant_info,
            user_info=self.user_info,
            tools=self.tool.tools
        )
        return self.agent_info

    def display_agent_info(self) -> None:
        """Agentの情報を表示する関数"""
        self.get_agent_info()
        print(self.agent_info)

    def get_agent_prompt(self) -> list:
        """Agentのプロンプトを取得する関数"""
        return self.prompt_template.get_prompt()

    def display_agent_prompt(self) -> None:
        """Agentのプロンプトを表示する関数"""
        self.prompt_template.display_prompt()



if __name__ == "__main__":
    import asyncio

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
    )
    agent.assistant_info = "あなたは優秀な校正者です。"
    agent.tool.set_tools(tools)

    # result = agent.invoke("magic function に３")
    # print(result)

    async def main() -> None:
        async for output in agent.stream("magic function に３", 5):
            print(output.output)

    asyncio.run(main())
