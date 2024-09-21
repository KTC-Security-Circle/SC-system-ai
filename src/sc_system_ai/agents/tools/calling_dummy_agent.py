# dummyAgentの呼び出しを行うツール

import logging

from sc_system_ai.template.user_prompts import User
from sc_system_ai.template.calling_agent import CallingAgent
from sc_system_ai.agents.official_absence_agent import DummyAgent

logger = logging.getLogger(__name__)


class CallingDummyAgent(CallingAgent):
    name = "calling_dummy_agent"
    description = "ダミーエージェントを呼び出すツール"

    def set_agent(self):
        return DummyAgent

calling_dummy_agent = CallingDummyAgent()

if __name__ == "__main__":
    from sc_system_ai.logging_config import setup_logging
    setup_logging()

    calling_dummy_agent.set_user_info(User(name="hogehoge", major="fugafuga専攻"))
    print(calling_dummy_agent.invoke({"user_input": "こんにちは"}))