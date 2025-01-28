# ダミーのエージェント
from typing import cast

from langchain_openai import AzureChatOpenAI

# from sc_system_ai.agents.tools import magic_function
from sc_system_ai.agents.tools.submit_official_absence import submit_official_absence
from sc_system_ai.template.agent import Agent
from sc_system_ai.template.ai_settings import llm
from sc_system_ai.template.user_prompts import User

dummy_agent_tools = [
    # magic_function
    submit_official_absence
]
dummy_agent_info = """あなたの役割は公欠届を提出することです。
公欠届の提出にはsubmit_official_absence関数を使用してください。

公欠届の提出に必要な情報とフォーマットは以下の通りです。
- 名前
    user_infoから取得してください
    ユーザーの名前のみ
- 日付
    MM/DDの形式
- 欠席する授業のリスト
    リストにする
    1限目から6限目まで順に挿入
    授業がない場合は空文字を挿入

    ["", "授業名/講師名", "", "授業名/講師名", "", ""]
- 欠席理由
    欠席理由のみ
    文章の長さは問いません

これらの情報が不足している場合は、提出してはいけません。
その場合は、ユーザーに不足している情報を求めてください。


全ての情報が揃ったらユーザーに入力内容の確認を取り、肯定的な返答があった場合のみ提出してください。
ユーザーから修正があった場合は、修正内容に従ってください。

提出後、または途中でユーザーから取り消しの旨があった場合、あなたはそれまでの情報を破棄してください。
"""

# agentクラスの作成


class DummyAgent(Agent):
    def __init__(
            self,
            llm: AzureChatOpenAI = llm,
            user_info: User | None = None,
    ):
        super().__init__(
            llm=llm,
            user_info=user_info if user_info is not None else User(),
        )
        self.assistant_info = dummy_agent_info
        super().set_assistant_info(self.assistant_info)
        self.set_tools(dummy_agent_tools)



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
        dummy_agent = DummyAgent(user_info=user_info)
        # classify_agent.display_agent_info()
        # print(main_agent.get_agent_prompt())
        # classify_agent.display_agent_prompt()

        user = input("ユーザー: ")
        if user == "exit":
            break

        # 通常の呼び出し
        # resp = classify_agent.invoke(user)
        # print(resp)

        # ストリーミング呼び出し
        for output in dummy_agent.invoke(user):
            print(output)
        resp = dummy_agent.get_response()

        if resp.error is not None:
            new_conversation = [
                ("human", user),
                ("ai", cast(str, resp.output))
            ]
            user_info.conversations.add_conversations_list(new_conversation)
