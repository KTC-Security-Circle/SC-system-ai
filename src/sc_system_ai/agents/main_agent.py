from langchain_openai import AzureChatOpenAI

from sc_system_ai.template.user_prompts import User
from sc_system_ai.template.ai_settings import llm
from sc_system_ai.template.agent import Agent
from sc_system_ai.agents.tools import magic_function

main_agent_tools = [magic_function]
main_agent_info = "あなたの役割はメインのエージェントです。"

# agentクラスの作成
class MainAgent(Agent):
    def __init__(
            self,
            llm: AzureChatOpenAI = llm,
            user_info: User = User(),
            assistant_info: str = main_agent_info,
            tools: list = main_agent_tools,
            ):
        super().__init__(
            llm=llm, 
            user_info=user_info, 
            assistant_info=assistant_info, 
            tools=tools
            )



if __name__ == "__main__":
    main_agent = MainAgent()
    print(main_agent.get_agent_info())
    print(main_agent.invoke("magic function に３をいれて"))