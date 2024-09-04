import logging

from typing import Type
from langchain.pydantic_v1 import BaseModel, Field
from langchain_core.tools import BaseTool
from langchain_core.output_parsers import StrOutputParser

from sc_system_ai.template.ai_settings import llm


logger = logging.getLogger(__name__)



#----- キーフレーズ抽出で分析 -----
def keyword_extraction(input: str) -> str:

    requiremments_prompt = f"""
    以下の条件に従い、文章からキーフレーズを抽出してください。

    条件:
        - キーフレーズは単語で構成される
        - キーフレーズはカンマ区切りで出力する

    文章:
    {input}
    """

    chain = llm | StrOutputParser()
    res = chain.invoke(requiremments_prompt)
    logger.debug(f"キーワード抽出の結果: {res}")
    return res

def classify_role_keyword(user_input: str, role_list: list[str]) -> str:
    role_type = ""

    keyword_list = keyword_extraction(user_input).split(",")

    for keyword in keyword_list:
        for check_role in role_list:
            if keyword in check_role:
                role_type = check_role
                break

    return role_type

#----- 類似度で分析 -----
def keyword_similarity(keyword: str, check_list: list[str]) -> str:

    requiremments_prompt = f"""
    文章と単語のリストを与えます。条件に従いリストの中から文章に最も関連性が高い単語を教えてください。

    文章:
    {keyword}

    リスト:
    [{",".join(check_list)}]

    条件:
        - 手順やアルゴリズムの説明、単語の関連度などの情報は不要です
        - 関連性のある単語がリストの中に存在する場合はその単語のみを出力してください
        - リストの中の単語と文章が明らかに関連性のない場合は、リストの中に存在する単語を出力しないでください
    """

    chain = llm | StrOutputParser()
    res = chain.invoke(requiremments_prompt)
    logger.debug(f"キーワード類似度の結果: {res}")
    return res

def classify_role_similarity(user_input: str, role_list: list[str]) -> str:
    role_type = ""

    similarity_word = keyword_similarity(user_input, role_list)

    for check_role in role_list:
        if check_role in similarity_word:
            role_type = check_role
            break

    return role_type


#----- 分析の流れ -----
# ユーザー入力を受け取り、キーワード抽出、類似度の順に分析を実行する
def classify_flow(user_input: str, role_list: list[str]) -> str:
    result = ""

    result = classify_role_keyword(user_input, role_list)
    if result == "":
        result = classify_role_similarity(user_input, role_list)

    return result



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
    input: str = Field(description="ユーザー入力")
    role_data: dict[str, list[str]] = Field(dammy_role_data, description="キーが大別されたタスク、値が詳細なタスクのリスト")
    

class ClassifyRoleTool(BaseTool):
    name = "classify_role_tool"
    description = "ユーザーの入力から役割を分類する"
    args_schema: Type[BaseModel] = ClassifyRoleInput

    def _run(
            self,
            input: str,
            role_data: dict[str, list[str]]= dammy_role_data
    ) -> str:
        """use the tool."""
        logger.info(f"Classify Role Toolが次の値で呼び出されました: {input}")
        result_role = ""
        result_role_type = ""

        for role in role_data.keys():
            if role in input:
                result_role = role
                break

        if result_role != "":
            result_role_type = classify_flow(input, role_data[result_role])
        else:
            for role_type in role_data.values():
                result_role_type = classify_flow(input, role_type)
                if result_role_type != "":
                    result_role = [key for key, value in role_data.items() if value == role_type][0]
                    break

        if (result_role == "" and
            result_role_type == ""):
            return "該当なし"
        elif (result_role != "" and
            result_role_type == ""):
            return f"実行可能なタスク:\n{','.join(role_data[result_role])}"
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

    input = "申請したい"
    print(classify_role.invoke({"input": input}))
    