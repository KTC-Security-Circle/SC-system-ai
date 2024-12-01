from os import linesep

from pydantic import BaseModel, Field

from sc_system_ai.template.ai_settings import llm


class Output(BaseModel):
    session_name: str = Field(description="セッション名", max_length=50, min_length=5)

requiremments_prompt = """
# タスク
以下に与える会話からセッション名をつけてください。
セッション名は以下の基準を参考にしてください。

## 基準
1. 会話の主なトピックやテーマ
- 会話でユーザーが何を求めているか、どのような話題を中心にしているかを基に、簡潔な要約をタイトルにします。

2. 具体性と簡潔さ
- タイトルは分かりやすく、できるだけ短くします。ただし、内容が十分に伝わるようにしてください。

3. ユーザーの意図や目標
- 会話から読み取れるユーザーの目的や方向性を反映してください。

## 会話内容
"""

def create_prompt(conversation: list[tuple[str, str]]) -> str:
    prompt = requiremments_prompt
    for role, message in conversation:
        prompt += f"{role}: {message}{linesep}"
    return prompt

def session_naming(conversation: list[tuple[str, str]]) -> str:
    prompt = create_prompt(conversation)
    model = llm.with_structured_output(Output)

    resullt = model.invoke(prompt)

    if isinstance(resullt, Output):
        return resullt.session_name
    else:
        raise RuntimeError("セッション名の取得に失敗しました")


if __name__ == "__main__":
    con = [
        ("human", "公欠届を提出したいです。"),
        ("ai", "承知しました。公欠届の提出についてお手伝いします。まずは名前を教えてください。"),
    ]

    print(session_naming(con))
