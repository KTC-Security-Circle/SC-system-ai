"""
### Agentの基底クラス

Agentの基底クラスを作成します。このクラスは、エージェントの情報を保持し、エージェントを実行するための関数を提供します。

詳しい使用方法は `docs/make-agent.md` を参照してください。

"""
import logging
from sc_system_ai.logging_config import setup_logging

from langchain_openai import AzureChatOpenAI
from langchain.agents import create_tool_calling_agent, AgentExecutor

from sc_system_ai.template.ai_settings import llm
from sc_system_ai.template.user_prompts import User
from sc_system_ai.template.system_prompt import PromptTemplate
from sc_system_ai.agents.tools import magic_function, search_duckduckgo

# ロガーの設定
logger = logging.getLogger(__name__)

# 全てのAgentに共通するツール
template_tools = [search_duckduckgo]

# エージェント情報のテンプレート
agent_info = """
エージェント情報:
-------------------
    assistant_info: {assistant_info}
    user_info: {user_info}
    tools: {tools}
-------------------
"""

# Agentクラスの作成
class Agent:
    """
    Agentクラス

    Args:
        llm (AzureChatOpenAI, optional): OpenAIのモデル. Defaults to llm.
        user_info (User, optional): ユーザー情報. Defaults to User().
    """
    def __init__(
            self,
            llm: AzureChatOpenAI = llm,
            user_info: User = User(),
    ):
        self.llm = llm
        self.user_info = user_info

        # assistant_infoとtoolsは各エージェントで設定する
        self.assistant_info = None
        self.tools = template_tools

        self.prompt_template = PromptTemplate(assistant_info=self.assistant_info, user_info=self.user_info)

        self.get_agent_info()

    def set_tools(self, tools):
        """ツールを追加する関数"""
        self.tools += tools

    def set_assistant_info(self, assistant_info: str):
        """アシスタント情報を設定する関数"""
        self.assistant_info = assistant_info
        self.prompt_template.create_prompt(assistant_info=self.assistant_info)
    
    def invoke(self, message: str):
        """
        エージェントを実行する関数

        Args:
            message (str): ユーザーからのメッセージ
        """
        agent = create_tool_calling_agent(llm=self.llm, tools=self.tools, prompt=self.prompt_template.full_prompt)
        agent_executor = AgentExecutor(agent=agent, tools=self.tools)
        try: # エージェントの実行
            logger.info(f"エージェントの実行を開始します。\n-------------------\n")
            logger.debug(f"最終的なプロンプト: {self.prompt_template.full_prompt.messages}")
            result = agent_executor.invoke({
                "chat_history": self.user_info.conversations.format_conversation(),
                "messages": message, 
                })
        except Exception as e:
            logger.error(f"エージェントの実行に失敗しました。エラー内容: {e}")
            result = "エージェントの実行に失敗しました。"
        return result
    
    def get_agent_info(self):
        """Agentの情報を取得する関数"""
        self.agent_info = agent_info.format(
            assistant_info=self.assistant_info,
            user_info=self.user_info,
            tools=self.tools
        )
        return self.agent_info
    
    def display_agent_info(self):
        """Agentの情報を表示する関数"""
        self.get_agent_info()
        print(self.agent_info)
    
    def get_agent_prompt(self):
        """Agentのプロンプトを取得する関数"""
        return self.prompt_template.get_prompt()
    
    def display_agent_prompt(self):
        """Agentのプロンプトを表示する関数"""
        self.prompt_template.display_prompt()



if __name__ == "__main__":
    # ユーザー情報
    user_name = "hogehoge"
    user_major = "fugafuga専攻"
    history = [
        ("human", "こんにちは!"),
        ("ai", "本日はどのようなご用件でしょうか？")
    ]
    user_info = User(name=user_name, major=user_major)
    user_info.conversations.add_conversations_list(history)

    tools = [magic_function]
    agent = Agent(
        user_info=user_info,
        assistant_info="あなたは優秀な校正者です。", 
        tools=tools, 
        llm=llm
    )
    
    result = agent.invoke("magic function に３")
    print(result)
