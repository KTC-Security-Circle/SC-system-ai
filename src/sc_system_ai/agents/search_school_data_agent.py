from collections.abc import Iterator
from typing import cast

from langchain_openai import AzureChatOpenAI

# from sc_system_ai.agents.tools import magic_function
from sc_system_ai.agents.tools.search_school_data import search_school_database_cosmos
from sc_system_ai.template.agent import Agent, AgentResponse
from sc_system_ai.template.ai_settings import llm
from sc_system_ai.template.user_prompts import User

# search_school_data_agent_tools = [
#     # magic_function,
# ]

search_school_data_agent_info = """あなたの役割は学校の情報をもとにユーザーの質問に回答することです。
以下に学校の情報について示します。

## 学校の情報
"""

class SearchSchoolDataAgentResponse(AgentResponse):
    document_id: list[str]

# agentクラスの作成

class SearchSchoolDataAgent(Agent):
    def __init__(
            self,
            llm: AzureChatOpenAI = llm,
            user_info: User | None = None,
            is_streaming: bool = True,
            return_length: int = 5
    ):
        super().__init__(
            llm=llm,
            user_info=user_info if user_info is not None else User(),
            is_streaming=is_streaming,
            return_length=return_length
        )
        self.assistant_info = search_school_data_agent_info

    def invoke(self, message: str) -> Iterator[SearchSchoolDataAgentResponse]:
        # Agentクラスのストリーミングを改修後にストリーミング実装
        self.cancel_streaming()
        search = search_school_database_cosmos(message)
        ids = []
        for doc in search:
            self.assistant_info += f"### {doc.metadata['title']}\n" + doc.page_content + "\n"
            ids.append(doc.metadata["id"])
        super().set_assistant_info(self.assistant_info)

        resp = cast(AgentResponse, next(super().invoke(message)))
        yield {
            **resp,
            "document_id": ids
        }

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
    agent = SearchSchoolDataAgent(user_info=user_info, is_streaming=False)
    print(next(agent.invoke("京都テックについて教えて")))
