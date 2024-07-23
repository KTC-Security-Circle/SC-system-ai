"""
### ユーザー情報を保持するクラスとユーザー情報のプロンプトを生成するクラスを定義するモジュール

class:
    - User(ユーザーの情報を保持するクラス)
    - UserInfoPrompt(ユーザー情報のプロンプトを生成するクラス)
"""
from sc_system_ai.template.prompts import user_info_template


class User():
    """
    ### User class
    ユーザーの情報を保持するクラス

    Args:
        name (str): ユーザーの名前
        major (str): ユーザーの専攻
    
    Returns:
        str: 現在のユーザー情報
    """
    def __init__(
            self, 
            name: str = 'None', 
            major: str = 'None',
        ):
        self.name = name
        self.major = major

    def __str__(self) -> str:
        return f"name: {self.name}, major: {self.major},"

    def update_user(self, name: str, major: str) -> 'User':
        self.name = name
        self.major = major
        return self



class UserInfoPrompt():
    """
    ### UserInfoPrompt class
    ユーザー情報のプロンプトを生成するクラス
    
    Args:
        user_info (User): ユーザーの情報
    
    Returns:
        str: ユーザー情報のプロンプト
    """
    def __init__(self, user_info: User = None):
        self.user_info = user_info
        if user_info is not None:
            self.user_prompt = self._format()

    def __str__(self) -> str:
        if self.user_info is not None:
            return self.user_prompt
        else:
            return "No user args. Please format user args."
    
    def _format(self):
        return user_info_template.format(name=self.user_info.name, major=self.user_info.major)

    def format(self, user_info: User) -> str:
        self.user_info = user_info
        self.user_prompt = self._format()

    def create_user_prompt(self, user_name: str, user_major: str) -> str:
        self.user_info = User(user_name, user_major)
        self.user_prompt = self._format()
        return self.user_prompt
    
    def update_user_prompt(self, user_name: str, user_major: str) -> str:
        self.user_info.update_user(user_name, user_major)
        self.user_prompt = self._format()
        return self.user_prompt
    
    def get_user_info(self) -> User:
        return self.user_info




if __name__ == "__main__":
    user = User("yuki", "スーパーAIクリエイター専攻")
    print(user)
    user_prompt = UserInfoPrompt(user)
    # user_prompt.format(user)
    print(user_prompt)