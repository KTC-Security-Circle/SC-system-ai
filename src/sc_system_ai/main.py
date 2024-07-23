from sc_system_ai.template.ai_settings import llm 
from sc_system_ai.template.user_prompts import UserPrompt, User

# ユーザー情報
class Chat():
    def __init__(self, user_name, user_major, conversation, user_info: User = None,):
        self.user_name = user_name
        self.user_major = user_major
        self.conversation = conversation
        self.user_info = user_info


    def __str__(self):
        return f"user_name: {self.user_name}, user_major: {self.user_major}, conversation: {self.conversation},"
    
    def create_user_prompt(self):
        user = UserPrompt(self.user_name, self.user_major)
        return user

    def create_chat(self):
        user = UserPrompt(self.user_name, self.user_major)
        user_prompt = user.create_user_prompt()
        return user_prompt
    




if __name__ == "__main__":
    # ユーザー情報
    user_name = "yuki"
    user_major = "スーパーAIクリエイター専攻"
    conversation = [
        ("human", "こんにちは!"),
        ("ai", "本日はどのようなご用件でしょうか？"),
        ("human", "私の名前と専攻は何ですか？"),
    ]
    user = User(user_name, user_major)
    chat = Chat(user_name, user_major, conversation, user)