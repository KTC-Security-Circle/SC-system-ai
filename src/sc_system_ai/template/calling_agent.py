import logging

from typing import Type
from langchain.pydantic_v1 import BaseModel, Field, validator
from langchain_core.tools import BaseTool

from sc_system_ai.template.user_prompts import User
from sc_system_ai.template.agent import Agent

logger = logging.getLogger(__name__)


class CallingAgentInput(BaseModel):
    user_input: str = Field(description="ユーザーの入力")

class CallingAgent(BaseTool):
    """
    エージェントを呼び出すツール

    - 呼び出すエージェントはset_agentメソッドで設定
    - ツール名と説明は新たに定義
    ```python
    class CallingDummyAgent(CallingAgent):
        name = "calling_dummy_agent"
        description = "ダミーエージェントを呼び出すツール"

        def set_agent(self):
            return DummyAgent
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
    agent: Agent = Field(description="呼び出し対象のエージェント", default_factory=Agent)

    class Config:
        validate_assignment = True # 再代入時の型チェックを有効

    # agentフィールドのバリデータ
    @validator("agent")
    def check_agent(cls, v):
        if not isinstance(v, Agent):
            raise ValueError("set_agentの返却値はAgentクラス、またはAgentのサブクラスである必要があります。")
        return v

    def _run(
            self,
            user_input: str,
        ) -> str:
        logger.info(f"Calling Agent Toolが次の値で呼び出されました: {user_input}")
        logger.debug(f"Calling Agent Toolが次の値で呼び出されました: {user_input}")

        # エージェントの呼び出し
        try:
            self._call_agent()
        except Exception as e:
            logger.error(f"エージェントの呼び出しに失敗しました: {e}")
            raise e
        else:
            logger.info(f"エージェントの呼び出しに成功しました: {self.agent}")
            logger.debug(f"エージェントの呼び出しに成功しました: {self.agent}")

        resp = self.agent.invoke(user_input)

        return resp["output"] if type(resp) is dict else resp

    def _call_agent(self) -> None:
        """エージェントの呼び出し"""
        agent_cls = self.set_agent()

        if type(agent_cls) is not type:
            raise TypeError("set_agentメソッドではエージェントのクラスを返却する必要があります。")
        self.agent = agent_cls(user_info=self.user_info)

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

    def set_agent(self) -> type:
        """呼び出すエージェントの設定
        返却値を設定するエージェントのクラスに変更

        例:
        DummyAgentを設定する場合
        ```python
        def set_agent(self):
            return DummyAgent
        ```
        """
        return Agent



calling_agent = CallingAgent()

if __name__ == "__main__":
    from sc_system_ai.logging_config import setup_logging
    setup_logging()

    calling_agent.set_user_info(User(name="hogehoge", major="fugafuga専攻"))
    print(calling_agent.invoke({"user_input": "こんにちは"}))