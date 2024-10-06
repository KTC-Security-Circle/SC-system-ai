from typing import Type, Literal
from importlib import import_module

from sc_system_ai.template.ai_settings import llm
from sc_system_ai.template.agent import Agent
from sc_system_ai.template.user_prompts import User

AGENT = Literal["classify", "dummy"]

class Chat:
    def __init__(
        self,
        user_name: str,
        user_major: str,
        conversation: list[tuple[str, str]] = []
    ) -> None:
        self.user = User(name=user_name, major=user_major)
        self.user.conversations.add_conversations_list(conversation)

    def invoke(
        self,
        message: str,
        command: AGENT = "classify"
    ) -> str:
        agent = self._call_agent(command)
        resp = agent.invoke(message)
        return resp["output"] if type(resp) is dict else resp

    def _call_agent(self, command: AGENT) -> Type[Agent]:
        try:  
            module_name = f"sc_system_ai.agents.{command}_agent"  
            class_name = f"{command.capitalize()}Agent"  
            module = import_module(module_name)  
            agent_class = getattr(module, class_name)  
            return agent_class(llm=llm, user_info=self.user)  
        except (ModuleNotFoundError, AttributeError):  
            raise ValueError(f"エージェントが見つかりません: {command}")  
    
    




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
    
    # main()
    chat = Chat(
        user_name="hogehoge",
        user_major="fugafuga専攻",
        conversation=[
            ("human", "こんにちは!"),
            ("ai", "本日はどのようなご用件でしょうか？")
        ]
    )
    
    message = "私の名前と専攻は何ですか？"
    resp = chat.invoke(message=message, command="dummy")
