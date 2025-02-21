from langchain_openai import AzureChatOpenAI

from sc_system_ai.agents.tools import magic_function
from sc_system_ai.template.agent import Agent
from sc_system_ai.template.ai_settings import llm
from sc_system_ai.template.user_prompts import User

self_introduce_agent_tools = [magic_function]
self_introduce_agent_info = """
あなたの役割は私たちがユーザーに提供できるサービスについて紹介することです。
提供できるサービスについては以下のサービス一覧を参照してください。
ユーザーのメッセージ次第では全てのサービスについて言及する必要はありません。
ユーザーのメッセージに対して適切なサービスを提案してください。

#### サービス一覧

- ユーザーとの雑談
- 各種申請
    - 公欠届
- 学校の情報についての質問への回答

#### 注意点

ユーザーのメッセージへの回答の際に「サービス」という表現はしてはいけません。
"""

# agentクラスの作成


class SelfIntroduceAgent(Agent):
    def __init__(
            self,
            llm: AzureChatOpenAI = llm,
            user_info: User | None = None,
    ):
        super().__init__(
            llm=llm,
            user_info=user_info if user_info is not None else User(),
        )
        self.assistant_info = self_introduce_agent_info
        super().set_assistant_info(self.assistant_info)
        super().set_tools(self_introduce_agent_tools)


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

    agent = SelfIntroduceAgent(user_info=user_info)
    agent.display_agent_info()
    # print(main_agent.get_agent_prompt())
    agent.display_agent_prompt()
    print(agent.invoke("なにができますか？"))
