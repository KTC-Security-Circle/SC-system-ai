from langchain_core.prompts import PipelinePromptTemplate, PromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from sc_system_ai.template.ai_settings import llm


# システムプロンプトのテンプレート
full_system_template = """あなたは優秀なAIアシスタントです。
次に与えるあなたに関しての情報とユーザーに関しての情報をもとにユーザーと会話してください。

# あなたに関しての情報
{assistant_info}

# ユーザーに関しての情報
{user_info}
"""

# アシスタントの情報を入力するためのプロンプト
assistant_info_template = """あなたは京都テックという名前の学校に所属している先生です。
学生との会話を通じて、学生の学習をサポートすることがあなたの役割です。"""


# ユーザーの情報を入力するためのプロンプト
user_info_template = """name: {name},
major: {major}
"""

# chat用のプロンプトテンプレートを作成
prompt_template = ChatPromptTemplate.from_messages([
    ("system", full_system_template.format(assistant_info=assistant_info_template, user_info=user_info_template)), # システムプロンプト
    ("placeholder", "{conversation}")                                                                              # ユーザーとの会話
])

# 今のプロンプトテンプレートの入力変数を表示
print(prompt_template.input_variables)


# ユーザーとの会話履歴
conversation = [
    ("human", "こんにちは!"),
    ("ai", "本日はどのようなご用件でしょうか？"),
    ("human", "私の名前と専攻は何ですか？"),
]

# プロンプトテンプレートに値を入力
prompt_value = prompt_template.invoke(
    {
        "name": "yuki",
        "major": "スーパーAIクリエイター専攻",
        "conversation": conversation,
    }
)
# プロンプトテンプレートに値を入力した結果を表示
print(prompt_value)

# chainを作成
chain = prompt_template | llm | StrOutputParser()
# chainを実行
print(chain.invoke(
    {
        "name": "yuki",
        "major": "スーパーAIクリエイター専攻",
        "conversation": conversation,
    }
))