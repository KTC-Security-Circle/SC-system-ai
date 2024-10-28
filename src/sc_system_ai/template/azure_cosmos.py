import logging
import os
from typing import Any

from azure.cosmos import CosmosClient, PartitionKey
from dotenv import load_dotenv
from langchain_community.vectorstores.azure_cosmos_db_no_sql import (
    AzureCosmosDBNoSqlVectorSearch,
)
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

from sc_system_ai.template.ai_settings import embeddings

load_dotenv()

# ロガーの設定
logger = logging.getLogger(__name__)


# policyの設定
indexing_policy = {
    "indexingMode": "consistent",
    "includedPaths": [{"path": "/*"}],
    "excludedPaths": [{"path": '/"_etag"/?'}],
    "vectorIndexes": [{"path": "/embedding", "type": "quantizedFlat"}],
}

# vectorEmbeddingの設定
vector_embedding_policy = {
    "vectorEmbeddings": [
        {
            "path": "/embedding",
            "dataType": "float32",
            "distanceFunction": "cosine",
            "dimensions": 1536,
        }
    ]
}

# cosmosDBの設定
HOST = os.environ["AZURE_COSMOS_DB_ENDPOINT"]
KEY = os.environ["AZURE_COSMOS_DB_KEY"]
cosmos_client = CosmosClient(HOST, KEY)
database_name = os.environ["AZURE_COSMOS_DB_DATABASE"]
container_name = os.environ["AZURE_COSMOS_DB_CONTAINER"]
partition_key = PartitionKey(path="/id")
cosmos_container_properties = {"partition_key": partition_key}
cosmos_database_properties = {"id": database_name}


class CosmosDBManager(AzureCosmosDBNoSqlVectorSearch):
    """AzureCosmosDBNoSqlVectorSearchの設定を継承しcosmosDBの操作を行うための関数を追加したクラス"""

    def __init__(
        self,
        *,
        cosmos_client: CosmosClient = cosmos_client,
        embedding: Embeddings = embeddings,
        vector_embedding_policy: dict[str, Any] = vector_embedding_policy,
        indexing_policy: dict[str, Any] = indexing_policy,
        cosmos_container_properties: dict[str,
                                          Any] = cosmos_container_properties,
        cosmos_database_properties: dict[str,
                                         Any] = cosmos_database_properties,
        database_name: str = database_name,
        container_name: str = container_name,
        create_container: bool = False,
    ):
        super().__init__(
            cosmos_client=cosmos_client,
            embedding=embedding,
            vector_embedding_policy=vector_embedding_policy,
            indexing_policy=indexing_policy,
            cosmos_container_properties=cosmos_container_properties,
            cosmos_database_properties=cosmos_database_properties,
            database_name=database_name,
            container_name=container_name,
            create_container=create_container,
        )

    def read_all_documents(self) -> list[Document]:
        """全てのdocumentsを読み込む関数"""
        logger.info("全てのdocumentsを読み込みます")
        query = "SELECT c.id, c.text FROM c"
        items = list(self._container.query_items(
            query=query, enable_cross_partition_query=True))
        docs = []
        i = 1
        for item in items:
            text = item["text"]
            item["number"] = i
            i += 1
            docs.append(
                Document(page_content=text, metadata=item))
        logger.debug(f"{docs[0].page_content=}, \n\nlength: {len(docs)}")
        return docs

    def get_source_by_id(self, id: str) -> str:
        """idを指定してsourceを取得する関数"""
        logger.info(f"{id=}のsourceを取得します")
        item = self._container.read_item(item=id, partition_key=id)

        result = item.get("source")
        if type(result) is str:
            return result
        else:
            return "sourceが見つかりませんでした"



if __name__ == "__main__":
    from sc_system_ai.logging_config import setup_logging
    setup_logging()

    cosmos_manager = CosmosDBManager()
    query = "京都テック"
    # results = cosmos_manager.read_all_documents()
    results = cosmos_manager.similarity_search(query, k=1)
    print(results[0])

    # idで指定したドキュメントのsourceを取得
    ids = results[0].metadata["id"]
    print(f"{ids=}")
    doc = cosmos_manager.get_source_by_id(ids)
    print(doc)
