from queue import Queue
from threading import Thread
from langchain_openai import AzureChatOpenAI
from langchain.agents import create_tool_calling_agent, AgentExecutor

from sc_system_ai.template.ai_settings import llm
from sc_system_ai.template.user_prompts import User
from sc_system_ai.template.streaming_handler import (
    StreamingAgentHandler,
    StreamingToolHandler
)
from sc_system_ai.agents.main_agent import MainAgent

import logging

# ロガーの設定
logger = logging.getLogger(__name__)

class StreamingAgent(MainAgent):
    def __init__(
        self,
        llm: AzureChatOpenAI=llm,
        user_info: User=User(),
        return_length: int=5
    ):
        super().__init__(llm=llm, user_info=user_info)
        self.queue = Queue()
        self.handler = StreamingAgentHandler(self.queue)
        self.tool_handler = StreamingToolHandler(self.queue)
        self.return_length = return_length

    def agent_setup(self):
        self.llm.streaming = True
        self.llm.callbacks = [self.handler]

        for tool in self.tools:
            tool.callbacks = [self.tool_handler]

        agent = create_tool_calling_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt_template.full_prompt
        )
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            callbacks=[self.handler]
        )

    def invoke(self, message):
        self.agent_setup()
        thread = Thread(target=self.task, args=(message,))

        phrase = ""
        thread.start()
        try:
            while True:
                token = self.handler.queue.get()

                if token is None:
                    break

                phrase += token
                if len(phrase) >= self.return_length:
                    yield phrase
                    phrase = ""
        except Exception as e:
            logger.error(f"エラーが発生しました:{e}")
        finally:
            yield phrase

            #クリーンアップ
            if thread and thread.is_alive():
                thread.join()

    def task(self, message):
        try:
            result = self.agent_executor.invoke({
                "messages": message
            })
        except Exception as e:
            result = f"エラーが発生しました:{e}"
            raise e
        finally:
            logger.debug(f"実行結果:\n{result}")



if __name__ == "__main__":
    from sc_system_ai.logging_config import setup_logging
    setup_logging()

    user = User(name="hoge", major="fuga")
    agent = StreamingAgent(
        user_info=user,
        return_length=5
    )

    for output in agent.invoke("magic functionに3を入れて"):
        print(output)
