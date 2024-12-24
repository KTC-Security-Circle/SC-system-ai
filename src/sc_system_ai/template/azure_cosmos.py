import logging
import os
from datetime import datetime
from typing import Any, Literal, cast

from azure.cosmos import CosmosClient, PartitionKey
from dotenv import load_dotenv
from langchain_community.vectorstores.azure_cosmos_db_no_sql import (
    AzureCosmosDBNoSqlVectorSearch,
)
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

from sc_system_ai.template.ai_settings import embeddings
from sc_system_ai.template.document_formatter import md_formatter, text_formatter

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

    def _similarity_search_with_score(
        self,
        embeddings: list[float],
        k: int = 1,
        pre_filter: dict | None = None,
        with_embedding: bool = False
    ) -> list[tuple[Document, float]]:
        query = "SELECT "

        # If limit_offset_clause is not specified, add TOP clause
        if pre_filter is None or pre_filter.get("limit_offset_clause") is None:
            query += "TOP @limit "

        query += (
            "c.id, c[@embeddingKey], c.text, c.metadata, "
            "VectorDistance(c[@embeddingKey], @embeddings) AS SimilarityScore FROM c"
        )

        # Add where_clause if specified
        if pre_filter is not None and pre_filter.get("where_clause") is not None:
            query += " {}".format(pre_filter["where_clause"])

        query += " ORDER BY VectorDistance(c[@embeddingKey], @embeddings)"

        # Add limit_offset_clause if specified
        if pre_filter is not None and pre_filter.get("limit_offset_clause") is not None:
            query += " {}".format(pre_filter["limit_offset_clause"])
        parameters = [
            {"name": "@limit", "value": k},
            {"name": "@embeddingKey", "value": self._embedding_key},
            {"name": "@embeddings", "value": embeddings},
        ]

        docs_and_scores = []

        items = list(
            self._container.query_items(
                query=query, parameters=parameters, enable_cross_partition_query=True
            )
        )
        for item in items:
            text = item["text"]
            metadata = item["metadata"]

            # idをmetadataに追加
            metadata["id"] = item["id"]

            score = item["SimilarityScore"]
            if with_embedding:
                metadata[self._embedding_key] = item[self._embedding_key]
            docs_and_scores.append(
                (Document(page_content=text, metadata=metadata), score)
            )
        return docs_and_scores

    def create_document(
        self,
        text: str,
        text_type: Literal["markdown", "plain"] = "markdown"
    ) -> list[str]:
        """データベースに新しいdocumentを作成する関数"""
        logger.info("新しいdocumentを作成します")
        texts, metadatas = self._division_document(
            md_formatter(text) if text_type == "markdown" else text_formatter(text)
        )
        ids = self._insert_texts(texts, metadatas)
        return ids

    def _division_document(
        self,
        documents: list[Document]
    ) -> tuple[list[str], list[dict[str, Any]]]:
        """documentを分割する関数"""
        logger.info("documentを分割します")
        docs = []
        metadata = []
        for doc in documents:
            docs.append(doc.page_content)
            metadata.append(doc.metadata)
        return docs, metadata

    def update_document(
        self,
        id: str,
        text: str,
    ) -> str:
        """データベースのdocumentを更新する関数"""
        logger.info("documentを更新します")

        # metadataのupdated_atを更新
        query = "SELECT c.metadata FROM c WHERE c.id = @id"
        parameters = [{"name": "@id", "value": id}]
        item = self._container.query_items(
            query=query,
            parameters=cast(list[dict[str, Any]], parameters), # mypyがエラー吐くのでキャスト
            enable_cross_partition_query=True
        ).next()
        metadata = item["metadata"]
        metadata["updated_at"] = datetime.now().strftime("%Y-%m-%d")

        to_upsert = {
            "id": id,
            "text": text,
            self._embedding_key: self._embedding.embed_documents([text])[0],
            "metadata": metadata,
        }
        self._container.upsert_item(body=to_upsert)
        return id

    def read_all_documents(self) -> list[Document]:
        """全てのdocumentsとIDを読み込む関数"""
        logger.info("全てのdocumentsを読み込みます")
        query = "SELECT c.id, c.text FROM c"
        items = list(self._container.query_items(
            query=query, enable_cross_partition_query=True)
        )
        docs: list[Document] = []
        for item in items:
            text = item["text"]
            _id = item["id"]
            docs.append(
                Document(page_content=text, metadata={"id": _id})
            )
        return docs

    def get_source_by_id(self, id: str) -> str:
        """idを指定してsourceを取得する関数"""
        logger.info(f"{id=}のsourceを取得します")
        query = "SELECT c.text FROM c WHERE c.id = " + f"'{id}'"
        item = self._container.query_items(
            query=query, enable_cross_partition_query=True
        ).next()

        result = item["text"]
        if type(result) is str:
            return result
        else:
            return "sourceが見つかりませんでした"


if __name__ == "__main__":
    from sc_system_ai.logging_config import setup_logging
    setup_logging()

    cosmos_manager = CosmosDBManager()
    # query = "京都テック"
    # # results = cosmos_manager.read_all_documents()
    # results = cosmos_manager.similarity_search(query, k=1)
    # print(results[0])
    # print(results[0].metadata["id"])

    # # idで指定したドキュメントのsourceを取得
    # ids = results[0].metadata["id"]
    # print(f"{ids=}")
    # doc = cosmos_manager.get_source_by_id(ids)
    # print(doc)

    # documentを更新
    text = """ストリーミングレスポンスに対応するためにジェネレータとして定義されています。
エージェントが回答の生成を終えてからレスポンスを受け取ることも可能です。"""
    _id = "c55bb571-498a-4db9-9da0-e9e35d46906b"
    print(cosmos_manager.update_document(_id, text))
