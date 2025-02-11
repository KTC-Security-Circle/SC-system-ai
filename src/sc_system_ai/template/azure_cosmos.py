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

    def read_item(
        self,
        values: list[str] | None = None,
        condition: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """条件を指定してdocumentを読み込む関数"""
        logger.info("documentを読み込みます")

        query = "SELECT "
        if values is not None:
            query += ", ".join(["c." + value for value in values]) + " "
        else:
            query += "* "
        query += "FROM c"

        parameters = []
        if condition is not None:
            query += " WHERE"
            for key, value in condition.items():
                name = key if "." not in key else key.replace(".", "_")
                query += f" c.{key} = @{name}"
                parameters.append({"name": f"@{name}", "value": value})
                query += " AND"
            query = query[:-4]

        item = list(self._container.query_items(
            query=query,
            parameters=parameters if parameters else None,
            enable_cross_partition_query=True
        ))

        if not item:
            logger.error(f"{id=}のdocumentが見つかりませんでした")
            raise ValueError("documentが見つかりませんでした")
        return item

    def create_document(
        self,
        text: str,
        text_type: Literal["markdown", "plain"] = "markdown",
        title: str | None = None,
        source_id: int | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> list[str]:
        """データベースに新しいdocumentを作成する関数"""
        logger.info("新しいdocumentを作成します")
        if metadata is not None and source_id is not None:
            metadata.setdefault("source_id", source_id)
        texts, metadatas = self._division_document(
            md_formatter(text, title, metadata) if text_type == "markdown"
            else text_formatter(text, title=title, metadata=metadata)
        )
        ids = self._insert_texts(texts, metadatas)
        return ids

    def _division_document(
        self,
        documents: list[Document]
    ) -> tuple[list[str], list[dict[str, Any]]]:
        """documentを分割する関数"""
        docs, metadata = [], []
        for doc in documents:
            docs.append(doc.page_content)
            metadata.append(doc.metadata)
        return docs, metadata

    def update_document(
        self,
        source_id: int | None = None,
        text: str | None = None,
        text_type: Literal["markdown", "plain"] | None = None,
        title: str | None = None,
        metadata: dict[str, Any] | None = None,
        del_metadata: list[str] | None = None,
        is_patch: bool = False,
    ) -> list[str]:
        """データベースのdocumentを更新する関数"""
        logger.info("documentを更新します")
        # source_idを指定してdocumentを取得
        update_docs = self.read_item(values=["id", "metadata"], condition={"metadata.source_id": source_id})
        _id = cast(str, update_docs[0]["id"])
        result = [_id]
        for doc in update_docs:
            if doc["id"] not in result:
                result.append(cast(str, doc["id"]))
        item = update_docs[0]

        if title is not None:
            self._title_updater(_id, title, item["metadata"].get("group_id", None))

        if metadata is not None:
            self._metadata_updater(
                _id, metadata, del_metadata, None if is_patch else item["metadata"].get("group_id", None)
            )

        if text is not None:
            if text_type is None:
                raise TypeError("textを更新する際はtext_typeを指定してください。")
            result = self._text_updater(
                _id, text, text_type, source_id, metadata, item["metadata"].get("group_id", None)
            )

        if any([title, metadata, del_metadata]):
            date = datetime.now().strftime("%Y-%m-%d")
            patch = [{
                "op": "replace",
                "path": "/metadata/updated_at",
                "value": date
            }]
            for doc_id in result:
                self._container.patch_item(
                    item=doc_id, partition_key=doc_id, patch_operations=patch
                )

        return result

    def _title_updater(self, id: str, title: str, group_id: str | None = None) -> None:
        """titleを更新する関数"""
        if group_id is None:
            ids = [id]
        else:
            data = self.read_item(values=["id"], condition={"metadata.group_id": group_id})
            ids = [cast(str, d["id"]) for d in data]

        patch = [{
            "op": "replace",
            "path": "/metadata/title",
            "value": title
        }]
        for _id in ids:
            self._container.patch_item(
                item=_id, partition_key=_id, patch_operations=patch
            )

    def _metadata_updater(
        self,
        id: str,
        metadata: dict[str, Any],
        del_metadata: list[str] | None = None,
        group_id: str | None = None,
    ) -> None:
        """metadataを更新する関数"""
        if group_id is None:
            data = self.read_item(values=["metadata"], condition={"id": id})[0]
            prev_metadatas = [cast(dict[str, Any], data["metadata"])]
            ids = [id]
        else:
            datas = self.read_item(values=["id", "metadata"], condition={"metadata.group_id": group_id})
            prev_metadatas = [cast(dict[str, Any], d["metadata"]) for d in datas]
            ids = [cast(str, d["id"]) for d in datas]

        for _id, pm in zip(ids, prev_metadatas, strict=True):
            patch = self._create_patch(pm, metadata, [] if del_metadata is None else del_metadata)
            self._container.patch_item(
                item=_id, partition_key=_id, patch_operations=patch
            )

    def _create_patch(
        self,
        prev_metadata: dict[str, Any],
        new_metadata: dict[str, Any],
        del_metadata: list[str],
    ) -> list[dict[str, Any]]:
        """metadataの差分を取得しパッチ操作を定義する関数"""
        patch = []
        for dm in del_metadata:
            if dm in new_metadata:
                raise ValueError(f"metadata:{dm}は新しいmetadataに含まれています")
            if dm in prev_metadata:
                patch.append({
                    "op": "remove",
                    "path": f"/metadata/{dm}"
                })

        for key, value in new_metadata.items():
            if key not in prev_metadata:
                patch.append({
                    "op": "add",
                    "path": f"/metadata/{key}",
                    "value": value
                })
            elif prev_metadata[key] != value:
                patch.append({
                    "op": "replace",
                    "path": f"/metadata/{key}",
                    "value": value
                })
        return patch

    def _text_updater(
        self,
        id: str,
        text: str,
        text_type: Literal["markdown", "plain"],
        source_id: int | None = None,
        metadata: dict[str, Any] | None = None,
        group_id: str | None = None,
    ) -> list[str]:
        """textを更新する関数"""
        created_at = self.read_item(values=["metadata.created_at"], condition={"id": id})[0]["created_at"]
        if group_id is None:
            self.delete_document_by_id(id)
        else:
            data = self.read_item(values=["id"], condition={"metadata.group_id": group_id})
            for d in data:
                self.delete_document_by_id(d["id"])

        ids = self.create_document(text, text_type, metadata=metadata, source_id=source_id)
        patch = [{
            "op": "replace",
            "path": "/metadata/created_at",
            "value": created_at
        }]
        for _id in ids:
            self._container.patch_item(
                item=_id, partition_key=_id, patch_operations=patch
            )
        return ids

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
        try:
            item = self.read_item(values=["text"], condition={"id": id})
        except ValueError:
            return "documentが見つかりませんでした"
        result = item[0]["text"]
        return cast(str, result)


if __name__ == "__main__":
    from sc_system_ai.logging_config import setup_logging
    setup_logging()

    cosmos_manager = CosmosDBManager()
    query = "京都テック"
    # results = cosmos_manager.read_all_documents()
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
#     _id = "989af836-cf9b-44c7-93d2-deff7aeae51f"
#     print(cosmos_manager.update_document(_id, text))


    # cosmos_manager.update_document(
    #     id="98941def-479c-4292-ad68-1d6dd9f4800e",
    #     text=text,
    #     text_type="markdown",
    # )
    # cosmos_manager.update_document(
    #     id="98941def-479c-4292-ad68-1d6dd9f4800e",
    #     text=text,
    #     text_type="markdown",
    # )
