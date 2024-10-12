# ダミーのツール

import logging

from typing import Type
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from langchain_core.output_parsers import StrOutputParser

from sc_system_ai.template.ai_settings import llm


logger = logging.getLogger(__name__)


def submit(
        name: str,
        date: str,
        classes: list[str],
        reason: str
    ) -> str:

    # --- 提出処理 ---
    print(
        f"""提出内容

        名前: {name}
        日付: {date}
        欠席理由: {reason}
        授業: {classes}
        """
    )
    
    return "公欠の申請が完了しました。"

class SubmitOfficialAbsenceInput(BaseModel):
    name: str = Field(description="ユーザーの名前")
    date: str = Field(description="欠席日")
    classes: list[str] = Field(
        description="""欠席する授業のリスト
        1限目から6限目まで順に挿入
        授業がない場合は空文字を挿入

        フォーマット:
        授業名/講師名
        """
    )
    reason: str = Field(description="欠席理由")

class SubmitOfficialAbsence(BaseTool):
    name = "submit_official_absence"
    description = "公欠届を提出するツール"
    args_schema: Type[BaseModel] = SubmitOfficialAbsenceInput

    def _run(
            self,
            name: str,
            date: str,
            classes: list[str],
            reason: str
    ):
        result = submit(
            name=name,
            date=date,
            classes=classes,
            reason=reason
        )

        return result
    
submit_official_absence = SubmitOfficialAbsence()
