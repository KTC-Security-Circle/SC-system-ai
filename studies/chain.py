from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# azure openai の設定をインポート
from sc_system_ai.template.ai_settings import llm

# テンプレート文章を定義し、プロンプトを作成
prompt = ChatPromptTemplate.from_messages([
    ("system", "あなたは優秀な校正者です。"),
    ("user", "次の文章に誤字があれば訂正してください。\n{sentences_before_check}")
])

# チェーンを作成
# prompt -> llm -> StrOutputParser という順番で処理を行う 
# "|" は処理の順番を示す 
chain = prompt | llm | StrOutputParser()

print(chain.invoke({"sentences_before_check": "こんんんちわ、これはテテストトです。"}))