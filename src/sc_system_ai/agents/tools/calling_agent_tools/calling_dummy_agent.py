# dummyAgentの呼び出しを行うツール

import logging

from sc_system_ai.agents.dummy_agent import DummyAgent
from sc_system_ai.template.calling_agent import CallingAgent
from sc_system_ai.template.user_prompts import User

logger = logging.getLogger(__name__)


class CallingDummyAgent(CallingAgent):
    def __init__(self) -> None:
        super().__init__()
        self.set_tool_info(
            name="calling_dummy_agent",
            description="ダミーエージェントを呼び出す。公欠届の提出を手伝う。",
            agent=DummyAgent
        )

calling_dummy_agent = CallingDummyAgent()

if __name__ == "__main__":
    from sc_system_ai.logging_config import setup_logging
    setup_logging()

    calling_dummy_agent.set_user_info(User(name="hogehoge", major="fugafuga専攻"))
    print(calling_dummy_agent.invoke({"user_input": "こんにちは"}))
