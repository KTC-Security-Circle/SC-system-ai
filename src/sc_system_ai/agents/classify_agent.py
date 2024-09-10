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
あなたの役割はユーザーの入力に対して、その入力がどのエージェントの役割かを特定し処理を引き継ぐことです。

ユーザーの入力から特定に失敗した場合、ユーザーに新しく入力を求めてください。

成功した場合、ふさわしいエージェントに処理を引き継いでください。
各エージェントは与えたツールで呼び出せます。
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

    def invoke(self, user_input: str) -> str:
        result = super().invoke(user_input)

        if type(result) is dict:
            now_conversation = [
                ("human", user_input),
                ("ai", result["output"])
            ]
            self.user_info.conversations.add_conversations_list(now_conversation)

        return result


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
    print(classify_agent.invoke("甲子園最高だね"))

