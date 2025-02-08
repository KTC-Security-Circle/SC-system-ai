import logging
import os

from dotenv import load_dotenv
from langchain_community.retrievers import AzureAISearchRetriever
from langchain_core.documents import Document
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from sc_system_ai.template.ai_settings import llm
from sc_system_ai.template.azure_cosmos import CosmosDBManager

load_dotenv()



logger = logging.getLogger(__name__)


class Output(BaseModel):
    word: str = Field(description="検索ワード")

def genarate_search_word(message: str) -> str:
    """メッセージから検索ワードを生成する関数"""
    prompt = """# Task
条件に従い以下に与えるメッセージから検索ワードを生成してください。

## 条件
- 検索ワードは日本語であること
- ユーザーが知りたい事に、直結するワードであること
- 複数を半角スペースで区切っても構いません

## メッセージ"""
    model = llm.with_structured_output(Output)
    result = model.invoke(prompt + "\n" + message)
    if isinstance(result, Output):
        logger.info(f"検索ワードの生成に成功しました: {result.word}")
        return result.word
    else:
        logger.error("検索ワードの生成に失敗しました")
        return message

def search_school_database_aisearch(search_word: str) -> list[Document]:
    """学校に関する情報を検索する関数(過去のデータベースを参照)"""
    retriever = AzureAISearchRetriever(
        service_name=os.environ["AZURE_AI_SEARCH_SERVICE_NAME"],
        index_name=os.environ["AZURE_AI_SEARCH_INDEX_NAME"],
        api_key=os.environ["AZURE_AI_SEARCH_API_KEY"],
        content_key="content",
        top_k=3
    )
    return retriever.invoke(search_word)

def search_school_database_cosmos(search_word: str, top_k: int = 2) -> list[Document]:
    """学校に関する情報を検索する関数(現在のデータベースを参照)"""
    cosmos_manager = CosmosDBManager()
    docs = cosmos_manager.similarity_search(search_word, k=top_k)
    return docs


class SearchSchoolDataInput(BaseModel):
    search_word: str = Field(description="学校に関する情報を検索するためのキーワード")


class SearchSchoolDataTool(BaseTool):
    name: str = "search_school_data_tool"
    description: str = "学校に関する情報を検索するためのツール"
    args_schema: type[BaseModel] = SearchSchoolDataInput

    def _run(
            self,
            search_word: str,
    ) -> list[str]:
        """use the tool."""
        logger.info(f"Search School Data Toolが次の値で呼び出されました: {search_word}")
        result = search_school_database_cosmos(search_word)
        search_result = []
        for i, doc in enumerate(result):
            if hasattr(doc, 'page_content'):
                search_result.append(
                    f'・検索結果{i + 1}は以下の通りです。\n{doc.page_content}\n参考URL: "{doc.metadata["id"]}"\n\n'
                )
        return search_result


search_school_data = SearchSchoolDataTool()

if __name__ == "__main__":
    from sc_system_ai.logging_config import setup_logging
    setup_logging()
    print(search_school_data.invoke({"search_word": "学校"}))
