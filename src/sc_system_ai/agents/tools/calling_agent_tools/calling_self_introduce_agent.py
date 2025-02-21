import logging

from sc_system_ai.agents.self_introduce_agent import SelfIntroduceAgent
from sc_system_ai.template.calling_agent import CallingAgent
from sc_system_ai.template.user_prompts import User

logger = logging.getLogger(__name__)


class CallingSelfIntroduceAgent(CallingAgent):
    def __init__(self) -> None:
        super().__init__()
        self.set_tool_info(
            name="calling_self_introduce_agent",
            description="自己紹介を行うエージェントを呼び出す。どのようなサービスを提供できるかをユーザーに伝える。",
            agent=SelfIntroduceAgent,
        )

calling_self_introduce_agent = CallingSelfIntroduceAgent()

if __name__ == "__main__":
    from sc_system_ai.logging_config import setup_logging
    setup_logging()

    calling_self_introduce_agent.set_user_info(User(name="hogehoge", major="fugafuga専攻"))
    print(calling_self_introduce_agent.invoke({"user_input": "こんにちは"}))
