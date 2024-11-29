from os import linesep

from pydantic import BaseModel, Field

from sc_system_ai.template.ai_settings import llm


class Output(BaseModel):
    session_name: str = Field(description="セッション名", max_length=50, min_length=5)

requiremments_prompt = """
以下に与える会話からセッション名をつけてください。
セッション名はhumanの発言を基準にし、会話の内容を簡潔に表すものとします。

会話内容:
"""

def create_prompt(conversation: list[tuple[str, str]]) -> str:
    prompt = requiremments_prompt
    for role, message in conversation:
        prompt += f"{role}: {message}{linesep}"
    return prompt

def session_naming(history: list[tuple[str, str]]) -> str:
    prompt = create_prompt(history)
    model = llm.with_structured_output(Output)

    resullt = model.invoke(prompt)

    if isinstance(resullt, Output):
        return resullt.session_name
    else:
        raise RuntimeError("セッション名の取得に失敗しました")


if __name__ == "__main__":
    con = [
        ("human", "こんにちは!"),
        ("ai", "本日はどのようなご用件でしょうか？"),
        ("human", "公欠届を提出したいです。"),
        ("ai", "かしこまりました、まずはお名前を教えてください。"),
    ]

    print(session_naming(con))
