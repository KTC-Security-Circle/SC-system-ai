from dotenv import load_dotenv
from queue import Queue
from threading import Thread

from langchain.callbacks.base import BaseCallbackHandler
from langchain.agents import create_tool_calling_agent, AgentExecutor

from sc_system_ai.template.ai_settings import llm
from sc_system_ai.agents.tools.magic_function import magic_function
from sc_system_ai.template.system_prompt import PromptTemplate
from sc_system_ai.template.user_prompts import User

load_dotenv()

class StreamingHandler(BaseCallbackHandler):
    def __init__(self, queue: Queue):
        super().__init__()
        self.queue = queue
    
    def on_llm_new_token(self, token, **kwargs):
        if token:
            self.queue.put(token)

    def on_agent_finish(self, response, **kwargs):
        print("end")
        self.queue.put(None)

    def on_llm_error(self, error, **kwargs):
        self.queue.put(None)


def main():
    queue = Queue()
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
    def task():
        result = agent_executor.invoke({
            "messages": "magic functionに3を入れて"
        })
        print(result)

    thread = Thread(target=task)
    thread.start()

    resp = ""

    try:
        while True:
            token = queue.get()
            if token is None:
                break

            resp += token
            if len(resp) >= 5:
                yield resp
                resp = ""
    finally:
        yield resp
        if thread and thread.is_alive():
            thread.join()

for output in main():
    print(output)
