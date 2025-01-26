import asyncio
from queue import Queue
from threading import Thread
from typing import Any, AsyncIterator

from dotenv import load_dotenv
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.callbacks.base import BaseCallbackHandler

from sc_system_ai.agents.tools.magic_function import magic_function
from sc_system_ai.template.ai_settings import llm
from sc_system_ai.template.system_prompt import PromptTemplate
from sc_system_ai.template.user_prompts import User

load_dotenv()

class StreamingHandler(BaseCallbackHandler):
    def __init__(self, queue: Queue):
        super().__init__()
        self.queue = queue

    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        print(token)
        if token:
            self.queue.put(token)

    def on_agent_finish(self, finish, **kwargs: Any) -> None:
        print("end")
        self.queue.put(None)

    def on_llm_error(self, **kwargs: Any) -> None:
        self.queue.put(None)


async def main() -> AsyncIterator[str]:
    queue: Queue = Queue()
    handler = StreamingHandler(queue)

    llm.streaming=True
    llm.callbacks=[handler]

    user = User(name="hoge", major="fuga")
    prompt = PromptTemplate(user_info=user)
    tool = [magic_function]

    agent = create_tool_calling_agent(
        llm=llm,
        tools=tool,
        prompt=prompt.full_prompt
    )
    agent_executor = AgentExecutor(agent=agent, tools=tool, callbacks=[handler])
    def task() -> None:
        result = agent_executor.invoke({
            "messages": "悲しい歌を歌ってください"
        })
        print(result)

    thread = Thread(target=task)
    thread.start()

    resp = ""
    while True:
        if queue.empty():
            continue
        token = queue.get()
        if token is None:
            break
        resp += token
        if len(resp) > 1:
            yield resp
            resp = ""
    thread.join()
    yield resp

async def job() -> None:
    async for i in main():
        print(i)

if __name__ == "__main__":
    asyncio.run(job())

