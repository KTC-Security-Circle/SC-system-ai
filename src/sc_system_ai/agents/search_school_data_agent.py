from collections.abc import AsyncIterator

from langchain_openai import AzureChatOpenAI

# from sc_system_ai.agents.tools import magic_function
from sc_system_ai.agents.tools.search_school_data import search_school_database_cosmos
from sc_system_ai.template.agent import Agent, AgentResponse, StreamingAgentResponse
from sc_system_ai.template.ai_settings import llm
from sc_system_ai.template.user_prompts import User

# search_school_data_agent_tools = [
#     # magic_function,
# ]

search_school_data_agent_info = """あなたの役割は学校の情報をもとにユーザーの質問に回答することです。
以下に学校の情報について示します。

## 学校の情報
"""

# agentクラスの作成

class SearchSchoolDataAgent(Agent):
    def __init__(
            self,
            llm: AzureChatOpenAI = llm,
            user_info: User | None = None,
    ):
        super().__init__(
            llm=llm,
            user_info=user_info if user_info is not None else User(),
        )
        self.assistant_info = search_school_data_agent_info

    def _add_search_result(self, message: str) -> list[str]:
        search = search_school_database_cosmos(message)
        ids = []
        for doc in search:
            self.assistant_info += f"### {doc.metadata['title']}\n" + doc.page_content + "\n"
            ids.append(doc.metadata["id"])
        super().set_assistant_info(self.assistant_info)
        return ids

    def invoke(self, message: str) -> AgentResponse:
        # Agentクラスのストリーミングを改修後にストリーミング実装
        ids = self._add_search_result(message)
        resp = super().invoke(message)
        resp.document_id = ids
        return resp

    async def stream(self, message: str, return_length: int = 5) -> AsyncIterator[StreamingAgentResponse]:
        ids = self._add_search_result(message)
        async for resp in super().stream(message, return_length):
            yield resp
        self.result.document_id = ids

if __name__ == "__main__":
    from sc_system_ai.logging_config import setup_logging
    setup_logging()
    # ユーザー情報
    user_name = "hogehoge"
    user_major = "fugafuga専攻"
    history = [
        ("human", "こんにちは!"),
        ("ai", "本日はどのようなご用件でしょうか？")
    ]
    user_info = User(name=user_name, major=user_major)
    user_info.conversations.add_conversations_list(history)
    agent = SearchSchoolDataAgent(user_info=user_info)
    print(agent.invoke("京都テックについて教えて"))
