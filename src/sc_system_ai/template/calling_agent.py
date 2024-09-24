import logging

from typing import Type
from langchain.pydantic_v1 import BaseModel, Field
from langchain_core.tools import BaseTool

from sc_system_ai.template.user_prompts import User
from sc_system_ai.template.agent import Agent

logger = logging.getLogger(__name__)


class CallingAgentInput(BaseModel):
    user_input: str = Field(description="ユーザーの入力")

class CallingAgent(BaseTool):
    """
    エージェントを呼び出すツール

    - __init__をオーバーライドし、set_tool_infoメソッドでツール情報を設定
    ```python
    class CallingDummyAgent(CallingAgent):
        def __init__(self):
            super().__init__()
            self.set_tool_info(
                name="calling_dummy_agent",
                description="ダミーエージェントを呼び出すツール",
                agent=DummyAgent
            )
    ```

    - ユーザー情報は、set_user_infoメソッドで設定
    - ツールをインスタンス化した後にset_user_infoメソッドを呼び出す
    ```python
    calling_dummy_agent = CallingDummyAgent()
    calling_dummy_agent.set_user_info(
        User(name="hogehoge", major="fugafuga専攻")
)
    ```
    """

    name = "calling_agent"
    description = "エージェントを呼び出すツール"
    args_schema: Type[BaseModel] = CallingAgentInput

    user_info: User = Field(description="ユーザー情報", default=User())
    agent: Type[Agent] = Agent

    def __init__(self) -> None:
        super().__init__()

    class Config:
        validate_assignment = True # 再代入時の型チェックを有効

    def _run(
            self,
            user_input: str,
        ) -> str:
        logger.info(f"Calling Agent Toolが次の値で呼び出されました: {user_input}")

        # エージェントの呼び出し
        try:
            agent = self.agent(user_info=self.user_info)
        except Exception as e:
            logger.error(f"エージェントの呼び出しに失敗しました: {e}")
            raise e
        else:
            logger.debug(f"エージェントの呼び出しに成功しました: {self.agent}")

        resp = agent.invoke(user_input)
        return resp["output"] if type(resp) is dict else resp

    def set_user_info(self, user_info: User) -> None:
        """ユーザー情報の設定

        Args:
            user_info (User): ユーザー情報、Userクラスのインスタンス
        """
        self.user_info.update_user(
            name=user_info.name,
            major=user_info.major,
            conversations=user_info.conversations
        )

    def set_tool_info(
            self,
            name: str,
            description: str,
            agent: Type[Agent]
        ) -> None:
        """ツール情報の設定

        Args:
            name (str): ツール名
            description (str): ツールの説明
            agent (Type[Agent]): 呼び出すエージェントのクラス
        """
        self.name = name
        self.description = description
        self.agent = agent


calling_agent = CallingAgent()

if __name__ == "__main__":
    from sc_system_ai.logging_config import setup_logging
    setup_logging()

    calling_agent.set_user_info(User(name="hogehoge", major="fugafuga専攻"))
    print(calling_agent.invoke({"user_input": "こんにちは"}))