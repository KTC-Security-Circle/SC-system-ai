from collections.abc import AsyncIterator
from typing import cast

from langchain_openai import AzureChatOpenAI

# from sc_system_ai.agents.tools import magic_function
from sc_system_ai.agents.tools.calling_dummy_agent import calling_dummy_agent
from sc_system_ai.agents.tools.calling_search_school_data_agent import (
    CallingSearchSchoolDataAgent,
    calling_search_school_data_agent,
)
from sc_system_ai.agents.tools.calling_small_talk_agent import calling_small_talk_agent
from sc_system_ai.agents.tools.classify_role import classify_role
from sc_system_ai.template.agent import Agent, AgentResponse, StreamingAgentResponse
from sc_system_ai.template.ai_settings import llm
from sc_system_ai.template.calling_agent import CallingAgent
from sc_system_ai.template.user_prompts import User

classify_agent_tools = [
    # magic_function,
    classify_role,
    calling_dummy_agent,
    calling_search_school_data_agent,
    calling_small_talk_agent,
]

classify_agent_info = """あなたの役割は適切なエージェントを選択し処理を引き継ぐことです。
あなたがユーザーと会話を行ってはいけません。
ユーザーの入力、会話の流れから適切なエージェントを選択してください。
引き継いだエージェントが処理を完了するまで、そのエージェントがユーザーと会話を続けるようにしてください。
"""

# agentクラスの作成


class ClassifyAgent(Agent):
    def __init__(
            self,
            llm: AzureChatOpenAI = llm,
            user_info: User | None = None,
    ):
        super().__init__(
            llm=llm,
            user_info=user_info if user_info is not None else User(),
        )
        self.assistant_info = classify_agent_info
        super().set_assistant_info(self.assistant_info)
        self.set_tools(classify_agent_tools)

    def set_tools(self, tools: list) -> None:
        # エージェント呼び出しツールにユーザー情報を設定
        for tool in tools:
            if isinstance(tool, CallingAgent):
                tool.set_user_info(self.user_info)
        super().set_tools(tools)

    def invoke(self, message: str) -> AgentResponse:
        # toolの出力がAgentReaponseで返って来るので整形
        for tool in self.tool.tools:
            if isinstance(tool, CallingAgent):
                tool.cancel_streaming()
        resp = super().invoke(message)
        resp.document_id = self._doc_id_checker()
        return resp

    def _doc_id_checker(self) -> list[str] | None:
        """
        ドキュメントIDが存在するか確認する
        """
        for tool in self.tool.tools:
            if isinstance(tool, CallingSearchSchoolDataAgent):
                if tool.document_id is not None:
                    return tool.document_id
        return None

    async def stream(self, message: str, return_length: int = 5) -> AsyncIterator[StreamingAgentResponse]:
        for tool in self.tool.tools:
            if isinstance(tool, CallingAgent):
                tool.setup_streaming(self.queue)
        async for output in super().stream(message, return_length):
            yield output


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

        # 通常の呼び出し
        resp = classify_agent.invoke(user)
        print(resp)

        # ストリーミング呼び出し
        # for output in classify_agent.invoke(user):
        #     print(output)
        # resp = classify_agent.get_response()

        if type(resp) is AgentResponse:
            new_conversation = [
                ("human", user),
                ("ai", cast(str,resp.output))
            ]
            user_info.conversations.add_conversations_list(new_conversation)
