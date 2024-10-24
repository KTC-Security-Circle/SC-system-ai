import logging
from typing import Literal

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from sc_system_ai.template.ai_settings import llm

logger = logging.getLogger(__name__)

#----- ユーザー入力から役割を分類するツール -----

#----- 類似度で分析 -----

# 類似度のしきい値
SIMILARITY_THRESHOLD = 0.5

class Output(BaseModel):
    word: Literal[
        # role
        "申請",
        # role_type
        "欠課届",
        "遅刻届",
        "遅延届",
        "早退届",
        "公欠届",
    ]
    similarity_score: float = Field(ge=0.0, le=1.0)

def keyword_similarity(
        sentence: str,
        keywords: list[str],
        llm = llm
    ) -> str:
    requiremments_prompt = f"""文章と単語のリストを与えます。
    条件に従いリストの中から文章に最も関連性が高い単語と類似度を教えてください。

    文章:
    {sentence}

    リスト:
    [{",".join(keywords)}]
    """
    llm = llm.with_structured_output(Output)
    result = llm.invoke(requiremments_prompt)

    logger.debug(f"キーワード類似度の結果: {result}")
    return result.word if result.similarity_score > SIMILARITY_THRESHOLD else ""

def classify_role_similarity(
        user_input: str,
        role_list: list[str]
    ) -> str:
    similarity_word = keyword_similarity(user_input, role_list)

    for check_role in role_list:
        if check_role in similarity_word:
            return check_role

    return ""

#----- 同じ単語が含まれているか確認 -----
def check_same_word(
        user_input: str,
        role_data: dict
    ) -> tuple[str, str]:
    for role, role_type in role_data.items():
        for check_role in role_type:
            if check_role[:-1] in user_input:
                return role, check_role

        if role in user_input:
            return role, ""

    return "", ""


dammy_role_data = {
    "申請": [
        "欠課届",
        "遅刻届",
        "遅延届",
        "早退届",
        "公欠届",
    ]
}

class ClassifyRoleInput(BaseModel):
    user_input: str = Field(description="ユーザー入力")

class ClassifyRoleTool(BaseTool):
    name: str = "classify_role_tool"
    description: str = "ユーザーの入力から役割を分類する"
    args_schema: type[BaseModel] = ClassifyRoleInput

    role_data: dict[str, list[str]] = Field(
        default=dammy_role_data,
        description="キーが大別されたタスク、値が詳細なタスクのリスト"
    )

    def _run(
            self,
            user_input: str,
    ) -> str:
        logger.info(f"Classify Role Toolが次の値で呼び出されました: {user_input}")

        result_role = ""
        result_role_type = ""

        result_role, result_role_type = check_same_word(user_input, self.role_data)

        if result_role_type == "":
            role_types = []
            for role_type in self.role_data.values():
                role_types += role_type

            result_role_type = classify_role_similarity(user_input, role_types)

        if result_role_type == "":
            roles = list(self.role_data.keys())
            result_role = classify_role_similarity(user_input, roles)
        else:
            result_role = [role for role, role_type in self.role_data.items() if result_role_type in role_type][0]

        if (result_role == "" and
            result_role_type == ""):
            return "分類結果: 該当なし"
        elif result_role_type == "":
            return f"可能性のあるタスク: {self.role_data[result_role]}"
        else:
            return f"分類結果:\n{result_role}.{result_role_type}"


classify_role = ClassifyRoleTool()

if __name__ == "__main__":
    from sc_system_ai.logging_config import setup_logging
    setup_logging()

    """
    dammy_role_data = {
        "申請": [
            "欠課届",
            "遅刻届",
            "遅延届",
            "早退届",
            "公欠届",
        ]
    }
    """

    input = "遅刻した"
    print(classify_role.invoke({"user_input": input}))
