from typing import Literal

from sc_system_ai.template.ai_settings import llm
from sc_system_ai.template.user_prompts import User

# エージェント
AGENTS = Literal[
    "分類",
    "ダミー",
]

def main(
    user_name: str,
    user_major: str,
    conversations: list[tuple[Literal["ai", "human"], str]],
    message: str,
    command: AGENTS = "分類",
):
    user_info = User(name=user_name, major=user_major)
    user_info.conversations.add_conversations_list(conversations)

    try:
        agent = create_agent(command, user_info)
        resp = agent.invoke(message=message)
    except Exception as e:
        raise e
    
    return resp


def create_agent(
    agent_name: AGENTS,
    user_info: User
):
    match agent_name:
        case "分類":
            from sc_system_ai.agents.classify_agent import ClassifyAgent
            agent = ClassifyAgent
        case "ダミー":
            from src.sc_system_ai.agents.official_absence_agent import DummyAgent
            agent = DummyAgent
        case _:
            raise ValueError(f"エージェントが存在しません: {agent_name}")
        
    return agent(llm=llm, user_info=user_info)



if __name__ == "__main__":
    from sc_system_ai.logging_config import setup_logging
    setup_logging()
    # ユーザー情報
    user_name = "hogehoge"
    user_major = "fugafuga専攻"
    conversation = [
        ("human", "こんにちは!"),
        ("ai", "本日はどのようなご用件でしょうか？")
    ]

    message = "私の名前と専攻は何ですか？"
    resp = main(user_name, user_major, conversation, message)
    print(resp)
