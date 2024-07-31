from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.tools import tool

from sc_system_ai.logging import logger
from sc_system_ai.template.ai_settings import llm
from sc_system_ai.template.prompts import full_system_template
from sc_system_ai.template.user_prompts import UserPromptTemplate, User, ConversationHistory
from sc_system_ai.template.system_prompt import PromptTemplate
from sc_system_ai.agents.tools import magic_function, search_duckduckgo

template_tools = [search_duckduckgo]

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
        assistant_info (str): エージェントの情報
        llm (AzureChatOpenAI, optional): OpenAIのモデル. Defaults to llm.
        user_info (User, optional): ユーザー情報. Defaults to User().
        tools (list, optional): ツール. Defaults to None.
    
    """
    def __init__(
            self,
            assistant_info: str,
            llm: AzureChatOpenAI = llm,
            user_info: User = User(),
            tools: list = [],
    ):
        self.llm = llm
        self.user_info = user_info
        self.assistant_info = assistant_info

        if tools is []:
            self.tools = template_tools
        else:
            self.tools = tools + template_tools

        self.full_prompt = PromptTemplate(assistant_info=assistant_info, user_info=self.user_info)

        self.get_agent_info()
    
    def invoke(self, message: str):
        """
        エージェントを実行する関数

        Args:
            message (str): ユーザーからのメッセージ
        """
        agent = create_tool_calling_agent(llm=self.llm, tools=self.tools, prompt=self.full_prompt.full_prompt)
        agent_executor = AgentExecutor(agent=agent, tools=self.tools)
        try:
            logger.info(f"エージェントの実行を開始します。\n-----------\n")
            result = agent_executor.invoke({
                "chat_history": self.user_info.conversations.format_conversation(),
                "messages": message, 
                })
        except Exception as e:
            logger.error(f"エージェントの実行に失敗しました。エラー内容: {e}")
            result = "エージェントの実行に失敗しました。"
        return result
    
    def get_agent_info(self):
        self.agent_info = agent_info.format(
    assistant_info=self.assistant_info,
    user_info=self.user_info,
    tools=self.tools
        )
        return self.agent_info



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

    tools = [magic_function.magic_function]
    agent = Agent(
        user_info=user_info,
        assistant_info="あなたは優秀な校正者です。", 
        tools=tools, 
        llm=llm
    )
    
    result = agent.invoke("magic function に３")
    print(result)
