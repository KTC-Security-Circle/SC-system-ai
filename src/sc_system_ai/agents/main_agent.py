from langchain_openai import AzureChatOpenAI

from sc_system_ai.agents.tools import magic_function
from sc_system_ai.template.agent import Agent
from sc_system_ai.template.ai_settings import llm
from sc_system_ai.template.user_prompts import User

main_agent_tools = [magic_function]
main_agent_info = "あなたの役割はメインのエージェントです。"

# agentクラスの作成


class MainAgent(Agent):
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
        self.assistant_info = main_agent_info
        super().set_assistant_info(self.assistant_info)
        super().set_tools(main_agent_tools)


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

    main_agent = MainAgent(user_info=user_info, is_streaming=False)
    main_agent.display_agent_info()
    # print(main_agent.get_agent_prompt())
    main_agent.display_agent_prompt()
    print(next(main_agent.invoke("magic function に３をいれて")))

