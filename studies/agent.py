from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import HumanMessage
from langchain import hub
from langchain.agents import create_tool_calling_agent
from langchain.agents import AgentExecutor

from sc_system_ai.template.ai_settings import llm

# 検索Toolを使って、検索する
# pip install duckduckgo-search
search = DuckDuckGoSearchRun()
input_message = "今の総理大臣は？"
print(search.run(input_message))

# toolをリストに追加
tools = [search]

# toolをモデルにバインド
# model_with_tools = llm.bind_tools(tools)

# モデルに入力
# response = model_with_tools.invoke([HumanMessage(content="こんにちは!")])
# response = model_with_tools.invoke([HumanMessage(content="今の総理大臣は？")])

# コンテンツとツールの呼び出しを表示
# print(f"ContentString: {response.content}")
# print(f"ToolCalls: {response.tool_calls}")

# プロンプトをlangchainhubから取得
prompt = hub.pull("hwchase17/openai-functions-agent")
print(prompt.messages)

# エージェントのもとを作成
agent = create_tool_calling_agent(llm, tools, prompt)

# エージェントがToolを実行できるようにする
agent_executor = AgentExecutor(agent=agent, tools=tools)

# エージェントを実行して表示
print(agent_executor.invoke({"input": input_message}))