from sc_system_ai.template.ai_settings import llm
from sc_system_ai.template.agent import Agent
from sc_system_ai.template.user_prompts import User

def main():
    # ユーザー情報
    user_name = "hogehoge"
    user_major = "fugafuga専攻"
    conversation = [
        ("human", "こんにちは!"),
        ("ai", "本日はどのようなご用件でしょうか？")
    ]

    # ユーザー情報を設定
    user = User(name=user_name, major=user_major)
    user.conversations.add_conversations_list(conversation)

    # エージェントの設定
    agent = Agent(llm=llm, user_info=user)

    # メッセージを送信
    message = "私の名前と専攻は何ですか？"
    resp = agent.invoke(message)
    print(resp)


if __name__ == "__main__":
    from sc_system_ai.logging_config import setup_logging
    setup_logging()
    
    main()
