import os
from dotenv import load_dotenv

from langchain_openai import AzureChatOpenAI
from langchain.callbacks.base import BaseCallbackHandler
from langchain.agents import create_tool_calling_agent, AgentExecutor

from sc_system_ai.agents.tools.magic_function import magic_function
from sc_system_ai.template.system_prompt import PromptTemplate
from sc_system_ai.template.user_prompts import User

load_dotenv()

class StreamingHandler(BaseCallbackHandler):
    def __init__(self):
        super().__init__()
    
    def on_llm_new_token(self, token, **kwargs):
        print(f"on_llm_new_token: {token}")

    def on_llm_end(self, response, **kwargs):
        print(f"on_llm_end: {response}")

    def on_llm_error(self, error, **kwargs):
        print(f"on_llm_error: {error}")

llm = AzureChatOpenAI(
    azure_deployment=os.environ['AZURE_DEPLOYMENT_NAME'],
    api_version=os.environ['OPENAI_API_VERSION'],
    streaming=True,
    callbacks=[StreamingHandler()]
)

user = User(name="hoge", major="fuga")
prompt = PromptTemplate(user_info=user)
tool = [magic_function]


agent = create_tool_calling_agent(
    llm=llm,
    tools=tool,
    prompt=prompt.full_prompt
)
agent_executor = AgentExecutor(agent=agent, tools=tool, callbacks=[StreamingHandler()])

result = agent_executor.invoke({"messages": "magic_functionに3"})
