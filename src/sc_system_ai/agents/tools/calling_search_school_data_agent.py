# dummyAgentの呼び出しを行うツール

import logging

from sc_system_ai.agents.search_school_data_agent import SearchSchoolDataAgent
from sc_system_ai.template.calling_agent import CallingAgent
from sc_system_ai.template.user_prompts import User

logger = logging.getLogger(__name__)


class CallingSearchSchoolDataAgent(CallingAgent):
    def __init__(self) -> None:
        super().__init__()
        self.set_tool_info(
            name="calling_search_school_data_agent",
            description="学校情報を検索するエージェントを呼び出すツール",
            agent=SearchSchoolDataAgent
        )

calling_search_school_data_agent = CallingSearchSchoolDataAgent()

if __name__ == "__main__":
    from sc_system_ai.logging_config import setup_logging
    setup_logging()

    calling_search_school_data_agent.set_user_info(User(name="hogehoge", major="fugafuga専攻"))
    print(calling_search_school_data_agent.invoke({"user_input": "京都テックについて教えて"}))
