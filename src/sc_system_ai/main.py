"""
### パッケージの使用例

以下の情報が必要となります。
- ユーザー名(str)
- 専攻(str)
- 会話履歴(List[Tuple[str, str]])
- is_streaming(bool): ストリーミングモードの有無. デフォルトはTrue
- return_length(int): ストリーミングモード時の返答数. デフォルトは5

```python
# ユーザー情報
user_name = "hogehoge"
user_major = "fugafuga専攻"
conversation = [
    ("human", "こんにちは!"),
    ("ai", "本日はどのようなご用件でしょうか？")
]
```


Chatクラスをインポートし、エージェントを呼び出せます。
```python
chat = Chat(
    user_name=user_name,
    user_major=user_major,
    conversation=conversation,
    is_streaming=False,
)

message = "私の名前と専攻は何ですか？"
resp = next(chat.invoke(message=message))
```


必要なモジュールをインポートして、エージェントを呼び出すこともできます。
```python
from sc_system_ai.template.agent import Agent
from sc_system_ai.template.user_prompts import User

# ユーザー情報を設定
user_info = User(name=user_name, major=user_major)
user.conversations.add_conversations_list(conversation)

# エージェントの設定
agent = Agent(user_info=user_info, is_streaming=False)

# メッセージを送信
message = "私の名前と専攻は何ですか？"
resp = next(agent.invoke(message))
```

各エージェントはagentsディレクトリに格納されています。
```python
from sc_system_ai.agents.classify_agent import ClassifyAgent
agent = ClassifyAgent(user_info=user)
```
"""

import logging
from collections.abc import AsyncIterator
from importlib import import_module
from typing import Literal, TypedDict

from sc_system_ai.template.agent import Agent
from sc_system_ai.template.ai_settings import llm
from sc_system_ai.template.user_prompts import User

logger = logging.getLogger(__name__)

AGENT = Literal["classify", "dummy", "search_school_data", "small_talk"]

class Response(TypedDict):
    output: str | None
    error: str | None
    document_id: list[str | int] | None

class StreamResponse(TypedDict):
    output: str | None
    error: str | None
    status: str | None

class Chat:
    """Chatクラス
    ユーザー情報と会話履歴を保持し、エージェントとのチャットを行うクラス

    Args:
        user_name (str): ユーザー名
        user_major (str): 専攻
        conversation (list[tuple[str, str]], optional): 会話履歴
        is_streaming (bool, optional): ストリーミングモードの有無
        return_length (int, optional): ストリーミングモード時の返答数

    Examples:
        ```python
        chat = Chat(
            user_name="hogehoge",
            user_major="fugafuga専攻",
            conversation=[
                ("human", "こんにちは!"),
                ("ai", "本日はどのようなご用件でしょうか？")
            ],
            is_streaming=False
        )

        # 通常呼び出し
        message = "私の名前と専攻は何ですか？"
        resp = next(chat.invoke(message=message))

        # ストリーミングモード
        is_streaming = True
        for r in chat.invoke(message=message, command="dummy"):
            print(r)
        chat.agent.get_response()
        ```
    """
    def __init__(
        self,
        user_name: str,
        user_major: str,
        conversation: list[tuple[str, str]] | None = None,
    ) -> None:
        self.user = User(name=user_name, major=user_major)
        if conversation is None:
            conversation = []

        self.user.conversations.add_conversations_list(conversation)
        self._agent: Agent | None = None

    @property
    def agent(self) -> Agent:
        if self._agent is None:
            logger.error("エージェントが設定されていません")
            raise ValueError("エージェントが設定されていません")
        return self._agent

    @agent.setter
    def agent(self, agent: Agent) -> None:
        if not isinstance(agent, Agent):
            logger.error("agentにはAgentクラス、またはそのサブクラスを代入してください")
            raise ValueError("agentにはAgentクラス、またはそのサブクラスを代入してください")
        self._agent = agent

    def invoke(
        self,
        message: str,
        command: AGENT = "classify"
    ) -> Response:
        """エージェントを呼び出し、チャットを行う関数

        Args:
            message (str): メッセージ
            command (AGENT, optional): 呼び出すエージェント。デフォルトでは分類エージェントを呼び出します。

        Returns:
            str: エージェントからの返答

        コマンドでエージェントを指定して、エージェントを呼び出す場合。
        ```python
        resp = next(chat.invoke(message="私の名前と専攻は何ですか？", command="dummy"))
        ```

        呼び出し可能なエージェント:
        - classify: 分類エージェント
        - dummy: ダミーエージェント
        """
        self._call_agent(command)
        resp = self.agent.invoke(message)
        return {
            "output": resp.output,
            "error": resp.error,
            "document_id": resp.document_id
        }

    async def stream(
        self,
        message: str,
        return_length: int = 5,
        command: AGENT = "classify"
    ) -> AsyncIterator[StreamResponse]:
        """エージェントを呼び出し、ストリーミングチャットを行う関数

        Args:
            message (str): メッセージ
            return_length (int, optional): ストリーミングモード時の返答数. デフォルトは5
            command (AGENT, optional): 呼び出すエージェント。デフォルトでは分類エージェントを呼び出します。

        Returns:
            Iterator[str]: エージェントからの返答

        コマンドでエージェントを指定して、エージェントを呼び出す場合。
        ```python
        for resp in chat.stream(message="私の名前と専攻は何ですか？", command="dummy"):
            print(resp)
        ```

        呼び出し可能なエージェント:
        - classify: 分類エージェント
        - dummy: ダミーエージェント
        """
        self._call_agent(command)
        async for resp in self.agent.stream(message, return_length):
            yield {
                "output": resp.output,
                "error": resp.error,
                "status": resp.status
            }

    def _call_agent(self, command: AGENT) -> None:
        try:
            module_name = f"sc_system_ai.agents.{command}_agent"
            class_name = "".join([cn.capitalize() for cn in command.split("_")]) + "Agent"
            module = import_module(module_name)
            agent_class = getattr(module, class_name)

            self.agent = agent_class(
                llm=llm,
                user_info=self.user,
            )
        except (ModuleNotFoundError, AttributeError, ValueError):
            logger.error(f"エージェントが見つかりません: {command}")
            raise ValueError(f"エージェントが見つかりません: {command}") from None


def static_chat() -> None:
    # ユーザー情報
    user_name = "hogehoge"
    user_major = "fugafuga専攻"
    conversation = [
        ("human", "こんにちは!"),
        ("ai", "本日はどのようなご用件でしょうか？")
    ]

    # ユーザー情報を設定
    user = User(name=user_name, major=user_major)
    user.conversations.add_conversations_list(conversation)

    # エージェントの設定
    agent = Agent(llm=llm, user_info=user)

    # メッセージを送信
    message = "私の名前と専攻は何ですか？"
    resp = agent.invoke(message)
    print(resp)



async def streaming_chat() -> None:
    # ユーザー情報
    user_name = "hogehoge"
    user_major = "fugafuga専攻"
    conversation = [
        ("human", "こんにちは!"),
        ("ai", "本日はどのようなご用件でしょうか？")
    ]

    # ユーザー情報を設定
    user = User(name=user_name, major=user_major)
    user.conversations.add_conversations_list(conversation)

    # エージェントの設定
    agent = Agent(llm=llm, user_info=user)

    # メッセージを送信
    message = "私の名前と専攻は何ですか？"
    async for resp in agent.stream(message):
        print(resp)


if __name__ == "__main__":
    # import asyncio

    from sc_system_ai.logging_config import setup_logging
    setup_logging()

    # static_chat()
    # streaming_chat()

    chat = Chat(
        user_name="hogehoge",
        user_major="fugafuga専攻",
        conversation=[
            ("human", "こんにちは!"),
            ("ai", "本日はどのようなご用件でしょうか？")
        ],
    )
    message = "AI・IT・ロボットワールドにある専攻について教えて"

    # try:
    #     resp = chat.agent.get_response()
    # except Exception:
    #     pass

    # 通常呼び出し
    resp = chat.invoke(message=message)
    print(resp)

    # # ストリーミング呼び出し
    # async def stream() -> None:
    #     async for r in chat.stream(message="京都テックについて教えて"):
    #         print(r)
    # asyncio.run(stream())

