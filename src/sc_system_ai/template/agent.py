from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool

from sc_system_ai.logging import logger
from sc_system_ai.template.ai_settings import llm
from sc_system_ai.template.prompts import full_system_template
from sc_system_ai.template.user_prompts import UserInfoPrompt, User, ConversationHistory
from sc_system_ai.agents.tools import magic_function


tools = [magic_function]


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
            self.create_user_prompt(user_info)

        if assistant_prompt is not None:
            self.create_assistant_prompt(assistant_prompt)

        self.tools = tools
        self.assistant_prompt = assistant_prompt

    def create_user_prompt(self, user_info: User):
        """ユーザープロンプトを作成する関数"""
        self.user_prompt = UserInfoPrompt(user_info)
        return self.user_prompt
    
    def create_assistant_prompt(self, assistant_prompt: str):
        """アシスタントプロンプトを作成する関数"""
        self.assistant_prompt = assistant_prompt
        return self.assistant_prompt
    
    def create_conversation_prompt(self, conversation_history: ConversationHistory):
        """会話履歴からプロンプトを作成する関数"""
        self.conversation_prompt = conversation_history.get_conversations()
        return self.conversation_prompt

    def create_system_prompt(self):
        """フルのシステムプロンプトを作成する関数"""
        if self.user_prompt is None: # ユーザープロンプトが設定されていない場合
            logger.error("ユーザープロンプトが設定されていません。create_user_promptメソッドを実行してユーザープロンプトを作成してください。")
            return
        if self.assistant_prompt is None: # アシスタントプロンプトが設定されていない場合
            logger.error("アシスタントプロンプトが設定されていません。create_assistant_promptメソッドを実行してアシスタントプロンプトを作成してください。")
            return
        
        conversation_history = self.create_conversation_prompt(conversation_history=self.user_info.conversations)
        
        self.full_system_prompt = full_system_template.format(
            assistant_info=self.assistant_prompt,
            user_info=self.user_prompt,
            )
        
        return self.full_system_prompt
    
    def show_system_prompt(self):
        """システムプロンプトを表示する関数"""
        prompt = self.create_system_prompt()
        print("full_system_prompt:\n", prompt)

    
    def run(self, message: str):
        """Agentの実行関数"""
        full_system_prompt = self.create_system_prompt()
        llm_with_tools = self.llm.bind_tools(self.tools)
        app = create_react_agent(model=self.llm, tools=self.tools)
        logger.info("Agentを実行します。")
        # messages = agent.invoke({"messages": [("user", message)]})
        # return messages




if __name__ == "__main__":
    # ユーザー情報
    user_name = "yuki"
    user_major = "スーパーAIクリエイター専攻"
    history = [
        ("human", "こんにちは!"),
        ("ai", "本日はどのようなご用件でしょうか？")
    ]
    user_info = User(name=user_name, major=user_major)
    user_info.conversations.add_conversations_list(history)
    agent = Agent(user_info=user_info, assistant_prompt="あなたは優秀な校正者です。", tools=tools, llm=llm)
    result = agent.run("私の名前と専攻は何ですか？")
    print(result)
