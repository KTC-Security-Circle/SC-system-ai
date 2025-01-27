import logging

from sc_system_ai.agents.small_talk_agent import SmallTalkAgent
from sc_system_ai.template.calling_agent import CallingAgent
from sc_system_ai.template.user_prompts import User

logger = logging.getLogger(__name__)


class CallingSmallTalkAgent(CallingAgent):
    def __init__(self) -> None:
        super().__init__()
        self.set_tool_info(
            name="calling_small_talk_agent",
            description="雑談エージェントを呼び出すツール",
            agent=SmallTalkAgent,
        )

calling_small_talk_agent = CallingSmallTalkAgent()

if __name__ == "__main__":
    from sc_system_ai.logging_config import setup_logging
    setup_logging()

    calling_small_talk_agent.set_user_info(User(name="hogehoge", major="fugafuga専攻"))
    print(calling_small_talk_agent.invoke({"user_input": "こんにちは"}))
