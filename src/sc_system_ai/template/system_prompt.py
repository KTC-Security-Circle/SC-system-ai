import logging

from langchain_core.prompts import ChatPromptTemplate

from sc_system_ai.template.prompts import assistant_info_template, full_system_template
from sc_system_ai.template.user_prompts import User, UserPromptTemplate

# ロガーの設定
logger = logging.getLogger(__name__)

class PromptTemplate:
    """
    フルのシステムプロンプトを作成するクラス

    Args:
    - full_system_template: システムプロンプトのテンプレート
    - assistant_info: アシスタントの情報を入力するためのプロンプト
    - user_info: ユーザーの情報を入力するためのプロンプト

    Methods:
    - create_prompt: フルのシステムプロンプトを作成する関数
    - get_prompt: フルのシステムプロンプトを取得する関数
    - display_prompt: プロンプトを表示する関数
    """
    def __init__(
            self,
            full_system_template: str = full_system_template,
            assistant_info: str = assistant_info_template,
            user_info: User | None = None,
            ):
        self.full_system_template = full_system_template
        self.assistant_info = assistant_info
        self.user_info = user_info if user_info is not None else User()

        self.user_info_prompt = UserPromptTemplate(user_info=self.user_info)

        self.full_prompt = self.create_prompt(assistant_info=self.assistant_info, user_info=self.user_info)

    def create_prompt(self, assistant_info: str | None = None, user_info: User | None = None) -> ChatPromptTemplate:
        """フルのシステムプロンプトを作成する関数"""
        if assistant_info is not None:
            self.assistant_info = assistant_info
            logger.debug(f"assistant_info setting: {self.assistant_info}")
        if user_info is not None:
            self.user_info = user_info
            logger.debug(f"user_info setting: {self.user_info}")

        formatted_system_prompt = self.full_system_template.format(
            assistant_info=self.assistant_info, user_info=self.user_info
            )
        self.full_prompt = ChatPromptTemplate.from_messages([
            ("system", formatted_system_prompt), # システムプロンプト
            ("placeholder", "{chat_history}"),  # ユーザーとの会話
            ("human", "{messages}"),
            ("placeholder", "{agent_scratchpad}"),
        ])
        return self.full_prompt

    def get_prompt(self) -> list:
        """フルのシステムプロンプトを取得する関数"""
        print(type(self.full_prompt.messages))
        return self.full_prompt.messages

    def display_prompt(self) -> None:
        """プロンプトを表示する関数"""
        print(f'prompts: {self.full_prompt.messages} \ninput_variables: {self.full_prompt.input_variables}')



if __name__ == "__main__":
    from sc_system_ai.logging_config import setup_logging
    setup_logging()
    user = User(name="hogehoge", major="fugafuga専攻")
    print(user)
    prompt = PromptTemplate(user_info=user)
    print(prompt.full_prompt)
    print(prompt.get_prompt())
