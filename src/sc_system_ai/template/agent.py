from langchain_openai import AzureChatOpenAI

from sc_system_ai.logging import logger
from sc_system_ai.template.ai_settings import llm
from sc_system_ai.template.prompts import full_system_template
from sc_system_ai.template.user_prompts import UserInfoPrompt, User


# Agentクラスの作成
class Agent:
    def __init__(
            self,
            llm: AzureChatOpenAI = llm,
            user_info: User = None,
            tools: list = None,
            assistant_prompt: str = None,
            ):
        self.llm = llm
        self.user_info = user_info
        if user_info is not None:
            self.user_prompt = self.create_user_prompt(user_info)

        self.tools = tools
        self.assistant_prompt = assistant_prompt

    def create_user_prompt(self, user_info: User):
        self.user_prompt = UserInfoPrompt(user_info)
        return self.user_prompt
    
    def create_assistant_prompt(self, assistant_prompt: str):
        self.assistant_prompt = assistant_prompt
        return self.assistant_prompt

    def create_system_prompt(self):
        if self.user_prompt is None: # ユーザープロンプトが設定されていない場合
            logger.error("ユーザープロンプトが設定されていません。create_user_promptメソッドを実行してユーザープロンプトを作成してください。")
            return 
        if self.assistant_prompt is None: # アシスタントプロンプトが設定されていない場合
            logger.error("アシスタントプロンプトが設定されていません。create_assistant_promptメソッドを実行してアシスタントプロンプトを作成してください。")
            return
        
        self.full_system_prompt = full_system_template.format(assistant_info=self.assistant_prompt, user_info=self.user_prompt, conversation=self.user_info.conversation)


if __name__ == "__main__":
    # ユーザー情報
    user_name = "yuki"
    user_major = "スーパーAIクリエイター専攻"
    user = User(user_name, user_major)
    user_prompt = UserInfoPrompt(user)
    user_info = user_prompt.create_user_prompt()

    # Agentの初期化
    agent = Agent(llm, user, user_info)
    print(agent.user_info)
    print(agent.tools)
    print(agent.prompt)
    print(agent.llm)
    print(agent.process("input_data"))
    print(agent.generate_output())