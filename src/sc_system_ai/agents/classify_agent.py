from langchain_openai import AzureChatOpenAI

from sc_system_ai.template.user_prompts import User
from sc_system_ai.template.ai_settings import llm
from sc_system_ai.template.agent import Agent
# from sc_system_ai.agents.tools import magic_function
from sc_system_ai.agents.tools.classify_role import classify_role

classify_agent_tools = [
    # magic_function,
    classify_role,
]


classify_agent_info = """
あなたの役割はユーザーの入力に対して、その入力がどのエージェントの役割かを判定し処理を引き継ぐことです。

ユーザーの入力から判定に失敗した場合、ユーザーに新しく入力を求めてください。
これは、判定に成功するまで繰り返してください。

判定に成功した後、どのエージェントがふさわしいかを出力してください。
"""

# agentクラスの作成


class ClassifyAgent(Agent):
    def __init__(
            self,
            llm: AzureChatOpenAI = llm,
            user_info: User = User()
    ):
        super().__init__(
            llm=llm,
            user_info=user_info
        )
        self.assistant_info = classify_agent_info
        super().set_assistant_info(self.assistant_info)
        super().set_tools(classify_agent_tools)


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

    classify_agent = ClassifyAgent(user_info=user_info)
    classify_agent.display_agent_info()
    # print(main_agent.get_agent_prompt())
    classify_agent.display_agent_prompt()
    print(classify_agent.invoke("早退の申請"))
    # print(classify_agent.invoke("甲子園最高だね"))

