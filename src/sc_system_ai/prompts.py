from langchain_core.prompts import PipelinePromptTemplate, PromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from sc_system_ai.template.ai_settings import llm
from sc_system_ai.template.prompts import full_system_template, assistant_info_template, user_info_template


prompt_template = ChatPromptTemplate.from_messages([
    # pipeline_system_prompt.final_prompt,
    ("system", full_system_template.format(assistant_info=assistant_info_template, user_info=user_info_template)),
    # ("system", "You are a helpful assistant"),
    ("placeholder", "{conversation}")
])

print(prompt_template.input_variables)

conversation = [
    ("human", "こんにちは!"),
    ("ai", "本日はどのようなご用件でしょうか？"),
    ("human", "私の名前と専攻は何ですか？"),
]

prompt_value = prompt_template.invoke(
    {
        "name": "yuki",
        "major": "スーパーAIクリエイター専攻",
        "conversation": conversation,
    }
)
print(prompt_value)

chain = prompt_template | llm | StrOutputParser()

print(chain.invoke(
    {
        "name": "yuki",
        "major": "スーパーAIクリエイター専攻",
        "conversation": conversation,
    }
))