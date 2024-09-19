from langchain_openai import AzureChatOpenAI

from sc_system_ai.template.user_prompts import User
from sc_system_ai.template.ai_settings import llm
from sc_system_ai.template.agent import Agent
# from sc_system_ai.agents.tools import magic_function
from sc_system_ai.agents.tools.classify_role import classify_role
# from sc_system_ai.agents.tools.calling_dummy_agent import calling_dummy_agent
from sc_system_ai.agents.tools.calling_agent import calling_agent

classify_agent_tools = [
    # magic_function,
    classify_role,
    # calling_dummy_agent,
]


classify_agent_info = """あなたの役割は適切なエージェントを選択し処理を引き継ぐことです。
ユーザーの入力から適切なエージェントを選択してください。
エージェントの選択はclassify_role関数の結果から判断してください。

エージェントを呼び出す際に必要な情報は、ユーザーに関しての情報を参照してください。

エージェントに処理を引き継いだ場合は、そのエージェントの出力をあなたの出力としてください。
これは、そのエージェントが処理を完了するまで続けてください。

適切なエージェントの選択、呼び出しができなかった場合は、そのままユーザーとの会話を続けてください。
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

    def invoke(self, user_input: str):
        resp = super().invoke(user_input)

        if type(resp) is dict:
        # --- respからエージェントを選択する処理 ---
            pass
        
        result = calling_agent(
            agent_name="dummyAgent",
            user_info=self.user_info,
            user_input=user_input
        )

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

    while True:
        classify_agent = ClassifyAgent(user_info=user_info)
        # classify_agent.display_agent_info()
        # print(main_agent.get_agent_prompt())
        # classify_agent.display_agent_prompt()

        user = input("ユーザー: ")
        if user == "exit":
            break

        resp = classify_agent.invoke(user)
        if type(resp) is dict:
            new_conversation = [
                ("human", user),
                ("ai", resp["output"])
            ]
            user_info.conversations.add_conversations_list(new_conversation)

        print(resp)

