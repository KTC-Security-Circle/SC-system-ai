from langchain_core.documents import Document
from langchain_community.retrievers import AzureAISearchRetriever
from langchain_core.tools import BaseTool
from langchain.pydantic_v1 import BaseModel, Field
from typing import Type, List
import logging
import os
from dotenv import load_dotenv
load_dotenv()


logger = logging.getLogger(__name__)


def search_school_database(search_word: str) -> List[Document]:
    """学校に関する情報を検索する関数"""
    retriever = AzureAISearchRetriever(
        service_name=os.environ["AZURE_AI_SEARCH_SERVICE_NAME"],
        index_name=os.environ["AZURE_AI_SEARCH_INDEX_NAME"],
        api_key=os.environ["AZURE_AI_SEARCH_API_KEY"],
        content_key="content",
        top_k=3
    )
    return retriever.invoke(search_word)


class SearchSchoolDataInput(BaseModel):
    search_word: str = Field(description="学校に関する情報を検索するためのキーワード")


class SearchSchoolDataTool(BaseTool):
    name = "search_school_data_tool"
    description = "学校に関する情報を検索するためのツール"
    args_schema: Type[BaseModel] = SearchSchoolDataInput

    def _run(
            self,
            search_word: str,
    ) -> List[str]:
        """use the tool."""
        logger.info(f"Search School Data Toolが次の値で呼び出されました: {search_word}")
        result = search_school_database(search_word)
        i = 1
        search_result = []
        for doc in result:
            # TODO: 参照したドキュメントの情報も返す形に変更予定
            if hasattr(doc, 'page_content'):
                search_result.append(
                    f'・検索結果{i}は以下の通りです。\n{doc.page_content}\n\n')
                i += 1
        return search_result


search_school_data = SearchSchoolDataTool()

if __name__ == "__main__":
    from sc_system_ai.logging_config import setup_logging
    setup_logging()
    print(search_school_data.invoke({"search_word": "学校"}))
