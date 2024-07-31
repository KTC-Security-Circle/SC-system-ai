"""
### ユーザー情報を保持するクラスとユーザー情報のプロンプトを生成するクラスを定義するモジュール

class:
    - User(ユーザーの情報を保持するクラス)
    - UserInfoPrompt(ユーザー情報のプロンプトを生成するクラス)
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Tuple
from langchain_core.messages import HumanMessage, AIMessage
from sc_system_ai.template.prompts import user_info_template


class Conversation(BaseModel):
    role: str = Field(description="発言者の役割 (human または ai)")
    content: str = Field(description="発言内容")

class ConversationHistory(BaseModel):
    conversations: List[Conversation] = Field(default_factory=list, description="会話履歴のリスト")
    def format_conversation(self) -> str:
        """
        会話履歴を整形して返す関数
        """
        chat_history = []
        for conversation in self.conversations:
            if conversation.role == "human":
                chat_history.append(HumanMessage(conversation.content))
            elif conversation.role == "ai":
                chat_history.append(AIMessage(conversation.content))
        return chat_history
    def get_conversations(self) -> List[Tuple[str, str]]:
        """
        会話履歴を取得する関数
        """
        return [(conversation.role, conversation.content) for conversation in self.conversations]

    def add_conversation(self, role: str, content: str):
        """
        会話履歴に新しい発言を追加する関数

        例：
        ```python
        user = User(name="test user", major="テスト専攻")
        user.conversations.add_conversation("human", "こんにちは!")
        ```
        """
        new_conversation = Conversation(role=role, content=content)
        self.conversations.append(new_conversation)
    
    def add_conversations_list(self, conversations: List[Tuple[str, str]]):
        """
        会話履歴にリスト形式の会話を追加する関数
        role: 発言者の役割 (human または ai)

        例：
        ```python
        user = User(name="test user", major="テスト専攻")
        conversations = [
            ("human", "こんにちは!"),
            ("ai", "本日はどのようなご用件でしょうか？")
        ]
        user.add_conversations_from_json(conversations)
        ```
        """
        for role, content in conversations:
            self.add_conversation(role, content)




class User(BaseModel):
    """
    ### User class
    ユーザーの情報を保持するクラス

    Args:
        name (str): ユーザーの名前
        major (str): ユーザーの専攻
        conversations (ConversationHistory): 会話履歴
    
    Returns:
        str: 現在のユーザー情報
    """
    name: str = Field(default='None', description="ユーザーの名前")
    major: str = Field(default='None', description="ユーザーの専攻")
    conversations: ConversationHistory = Field(default_factory=ConversationHistory, description="会話履歴")

    def __str__(self) -> str:
        return f"name: {self.name}, major: {self.major}, conversation: {self.conversations.get_conversations()}"

    def update_user(self, **kwags) -> 'User':
        for key, value in kwags.items():
            setattr(self, key, value)
        return self



class UserPromptTemplate:
    """
    ### UserInfoPrompt class
    ユーザー情報のプロンプトテンプレートを生成するクラス
    
    Args:
        user_info (User): ユーザーの情報
    
    Returns:
        str: ユーザー情報のプロンプトテンプレート
    """
    def __init__(self, user_info: Optional[User] = None):
        self.user_info = user_info
        if user_info is not None:
            self.user_prompt_template = self._format()
        else:
            self.user_prompt_template = None


    def __str__(self) -> str:
        if self.user_prompt_template is not None:
            return self.user_prompt_template
        else:
            return "No user args. Please format user args."
    
    def _format(self) -> str:
        return user_info_template.format(name=self.user_info.name, major=self.user_info.major)

    def format(self, user_info: User) -> str:
        self.user_info = user_info
        self.user_prompt_template = self._format()

    def create_user_prompt_template(self, user_name: str, user_major: str) -> str:
        self.user_info = User(user_name, user_major)
        self.user_prompt_template = self._format()
        return self.user_prompt_template
    
    def update_user_prompt_template(self, user_name: str, user_major: str) -> str:
        self.user_info.update_user(user_name, user_major)
        self.user_prompt_template = self._format()
        return self.user_prompt_template
    
    def get_user_info(self) -> User:
        return self.user_info
    
    def get_user_prompt_template(self) -> str:
        return self.user_prompt_template




if __name__ == "__main__":
    user = User(name="yuki", major="スーパーAIクリエイター専攻")
    print(user)
    user.update_user(name="update")
    user_prompt = UserPromptTemplate(user)
    # user_prompt.format(user)
    print(user_prompt)
    user.conversations.add_conversation("human", "こんにちは!")
    print(user.conversations)
    print(user.conversations.format_conversation())