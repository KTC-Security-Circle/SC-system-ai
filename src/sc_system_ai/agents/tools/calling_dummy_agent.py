# dummyAgentの呼び出しを行うツール

import logging

from typing import Type
from langchain.pydantic_v1 import BaseModel, Field
from langchain_core.tools import BaseTool

from sc_system_ai.template.user_prompts import User
from sc_system_ai.agents.official_absence_agent import DummyAgent

logger = logging.getLogger(__name__)
    

class CallingDummyAgentInput(BaseModel):
    user_input: str = Field(description="ユーザーの入力")

class CallingDummyAgent(BaseTool):
    name = "calling_dummy_agent"
    description = "ダミーエージェントを呼び出すツール"
    args_schema: Type[BaseModel] = CallingDummyAgentInput
    user_info: User = Field(description="ユーザー情報", default=User())

    def __init__(self):
        super().__init__()

    def _run(
            self,
            user_input: str,
        ) -> str:
        # ダミーエージェントの呼び出し
        agent = DummyAgent(user_info=self.user_info)
        resp = agent.invoke(user_input)

        return resp
    
    def set_user_info(self, user_info: User):
        self.user_info = user_info


calling_dummy_agent = CallingDummyAgent()

if __name__ == "__main__":
    from sc_system_ai.logging_config import setup_logging
    setup_logging()

    print(calling_dummy_agent.invoke({
        "user_input": "こんにちは", 
        "user_info": User(name="hogehoge", major="fugafuga専攻")
    }))