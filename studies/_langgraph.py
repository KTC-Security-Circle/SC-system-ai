from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from sc_system_ai.template.ai_settings import llm

# ツールの準備
@tool
def magic_function(input: int) -> int:
    """Applies a magic function to an input."""
    return input + 2

tools = [magic_function]

# クエリの準備
query = "what is the value of magic_function(3)?"

# ReactAgentExecutorの準備
app = create_react_agent(model=llm, tools=tools)

print(app.get_prompts())

# ReactAgentExecutorの実行
# messages = app.invoke({"messages": [("human", query)]})
# print({
#     "input": query,
#     "output": messages["messages"][-1].content,
# })