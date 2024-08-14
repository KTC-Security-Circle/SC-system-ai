from sc_system_ai.template.ai_settings import embeddings
from langchain_core.embeddings import Embeddings
from langchain_core.documents import Document
from langchain_community.vectorstores.azure_cosmos_db_no_sql import (
    AzureCosmosDBNoSqlVectorSearch,
)
import azure.cosmos.exceptions as exceptions
from azure.cosmos import CosmosClient, PartitionKey
from typing import List, Optional, Any, Dict
import os
from dotenv import load_dotenv
load_dotenv()


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

HOST = os.environ["AZURE_COSMOS_DB_ENDPOINT"]
KEY = os.environ["AZURE_COSMOS_DB_KEY"]

cosmos_client = CosmosClient(HOST, KEY)
database_name = os.environ["AZURE_COSMOS_DB_DATABASE"]
container_name = os.environ["AZURE_COSMOS_DB_CONTAINER"]
partition_key = PartitionKey(path="/id")
cosmos_container_properties = {"partition_key": partition_key}
cosmos_database_properties = {"id": database_name}


class CosmosManager(AzureCosmosDBNoSqlVectorSearch):

    def __init__(
        self,
        *,
        cosmos_client: CosmosClient = cosmos_client,
        embedding: Embeddings = embeddings,
        vector_embedding_policy: Dict[str, Any] = vector_embedding_policy,
        indexing_policy: Dict[str, Any] = indexing_policy,
        cosmos_container_properties: Dict[str,
                                          Any] = cosmos_container_properties,
        cosmos_database_properties: Dict[str,
                                         Any] = cosmos_database_properties,
        database_name: str = database_name,
        container_name: str = container_name,
        create_container: bool = False,
    ):
        """Custom constructor to initialize additional parameters."""
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

    def read_all_documents(self) -> List[Document]:
        """Read all documents from the CosmosDB."""
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
        return docs


if __name__ == "__main__":
    cosmos_manager = CosmosManager()
    query = "What were the compute requirements for training GPT 4"
    results = cosmos_manager.read_all_documents()
    print(results[0])
