"""
### パッケージの使用例

以下の情報が必要となります。
- ユーザー名(str)
- 専攻(str)
- 会話履歴(List[Tuple[str, str]])

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
    conversation=conversation
)

message = "私の名前と専攻は何ですか？"
resp = chat.invoke(message=message)
```


必要なモジュールをインポートして、エージェントを呼び出すこともできます。
```python
from sc_system_ai.template.agent import Agent
from sc_system_ai.template.user_prompts import User

# ユーザー情報を設定
user_info = User(name=user_name, major=user_major)
user.conversations.add_conversations_list(conversation)

# エージェントの設定
agent = Agent(user_info=user_info)

# メッセージを送信
message = "私の名前と専攻は何ですか？"
resp = agent.invoke(message)
```

各エージェントはagentsディレクトリに格納されています。
```python
from sc_system_ai.agents.classify_agent import ClassifyAgent
agent = ClassifyAgent(user_info=user)
```
"""

from typing import Type, Literal, Iterator
from importlib import import_module

from sc_system_ai.template.ai_settings import llm
from sc_system_ai.template.agent import Agent
from sc_system_ai.template.user_prompts import User

AGENT = Literal["classify", "dummy"]

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
            ]
        )

        message = "私の名前と専攻は何ですか？"
        resp = chat.invoke(message=message)
        ```
    """
    def __init__(
        self,
        user_name: str,
        user_major: str,
        conversation: list[tuple[str, str]] = [],
        is_streaming: bool = True,
        return_length: int = 5
    ) -> None:
        self.user = User(name=user_name, major=user_major)
        self.user.conversations.add_conversations_list(conversation)
        self.is_streaming = is_streaming
        self.return_length = return_length

    def invoke(
        self,
        message: str,
        command: AGENT = "classify"
    ) -> Iterator[str]:
        """エージェントを呼び出し、チャットを行う関数

        Args:
            message (str): メッセージ
            command (AGENT, optional): 呼び出すエージェント。デフォルトでは分類エージェントを呼び出します。

        Returns:
            str: エージェントからの返答

        コマンドでエージェントを指定して、エージェントを呼び出す場合。
        ```python
        resp = chat.invoke(message="私の名前と専攻は何ですか？", command="dummy")
        ```

        呼び出し可能なエージェント:
        - classify: 分類エージェント
        - dummy: ダミーエージェント
        """
        agent = self._call_agent(command)
        
        if self.is_streaming:
            yield from agent.invoke(message)
        else:
            resp = next(agent.invoke(message))
            yield resp["output"] if type(resp) is dict else resp

    def _call_agent(self, command: AGENT) -> Type[Agent]:
        try:  
            module_name = f"sc_system_ai.agents.{command}_agent"  
            class_name = f"{command.capitalize()}Agent"  
            module = import_module(module_name)  
            agent_class = getattr(module, class_name)

            if self.is_streaming:  
                agent = agent_class(
                    llm=llm,
                    user_info=self.user,
                    is_streaming=self.is_streaming,
                    return_length=self.return_length
                )
            else:
                agent = agent_class(llm=llm, user_info=self.user)
            return agent
        except (ModuleNotFoundError, AttributeError):  
            raise ValueError(f"エージェントが見つかりません: {command}")  



def static_chat():
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
    agent = Agent(llm=llm, user_info=user, is_streaming=False)

    # メッセージを送信
    message = "私の名前と専攻は何ですか？"
    resp = next(agent.invoke(message))
    print(resp)



def streaming_chat():
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
    agent = Agent(llm=llm, user_info=user, is_streaming=True)

    # メッセージを送信
    message = "私の名前と専攻は何ですか？"
    for resp in agent.invoke(message):
        print(resp)


if __name__ == "__main__":
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
        is_streaming=False,
    )
    message = "私の名前と専攻は何ですか？"
    

    # 通常呼び出し
    resp = next(chat.invoke(message=message, command="dummy"))
    print(resp)

    chat.is_streaming = True
    # ストリーミング呼び出し
    for r in chat.invoke(message=message, command="dummy"):
        print(r)

