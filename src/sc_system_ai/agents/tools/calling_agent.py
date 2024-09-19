import logging

from typing import Literal

from sc_system_ai.template.user_prompts import User
from sc_system_ai.template.agent import Agent
from sc_system_ai.agents.main_agent import MainAgent
from sc_system_ai.agents.official_absence_agent import DummyAgent

logger = logging.getLogger(__name__)


# エージェント
Agents = Literal[
    "mainAgent",
    "dummyAgent"
]

def match_agent(agent_name: Agents, user_info: User):
    match agent_name:
        case "mainAgent":
            return MainAgent(user_info=user_info)
        case "dummyAgent":
            return DummyAgent(user_info=user_info)
        case _:
            raise TypeError(f"エージェント{agent_name}は存在しません。")
        
def calling_agent(
        agent_name: Agents,
        user_info: User,
        user_input: str
    ) -> str | None:
    try:
        agent = match_agent(agent_name, user_info)
    except TypeError as e:
        logger.error(f"エージェントの呼び出しに失敗しました。: {e}")
        return None

    if isinstance(agent, Agent):
        resp = agent.invoke(user_input)

        return resp

if __name__ == "__main__":
    from sc_system_ai.logging_config import setup_logging
    setup_logging()

    print(calling_agent(
        agent_name="dummyAgent",
        user_info=User(name="hogehoge", major="fugafuga専攻"),
        user_input="こんにちは"
    ))