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


# Agentクラスの作成
class Agent:
    def __init__(
            self,
            llm: AzureChatOpenAI = llm,
            user_info: User = None,
            assistant_info: str = None,
            tools: list = None,
    ):
        self.llm = llm
        self.user_info = user_info
        self.assistant_info = assistant_info
        self.tools = tools

        self.full_prompt = PromptTemplate(assistant_info=assistant_info, user_info=self.user_info)
    
    def run(self, message: str):

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
            raise ValueError("エージェントの実行に失敗しました。時間をおいて再度お試しください。")
        return result



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
    
    result = agent.run("magic function に３")
    print(result)
