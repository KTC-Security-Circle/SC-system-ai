# https://python.langchain.com/v0.2/docs/integrations/vectorstores/azure_cosmos_db_no_sql/

import os
from dotenv import load_dotenv
load_dotenv()
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from azure.cosmos import CosmosClient, PartitionKey
from langchain_community.vectorstores.azure_cosmos_db_no_sql import (
    AzureCosmosDBNoSqlVectorSearch,
)
from langchain_openai import AzureOpenAIEmbeddings

# Load the PDF
# loader = PyPDFLoader("https://arxiv.org/pdf/2303.08774.pdf")
# data = loader.load()


# text_splitter = RecursiveCharacterTextSplitter(
#     chunk_size=1000, chunk_overlap=150)
# docs = text_splitter.split_documents(data)

# print(docs[0])


indexing_policy = {
    "indexingMode": "consistent",
    "includedPaths": [{"path": "/*"}],
    "excludedPaths": [{"path": '/"_etag"/?'}],
    "vectorIndexes": [{"path": "/embedding", "type": "quantizedFlat"}],
}

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


HOST = os.getenv("AZURE_COSMOS_DB_ENDPOINT")
KEY = os.getenv("AZURE_COSMOS_DB_KEY")

cosmos_client = CosmosClient(HOST, KEY)
database_name = "langchain_python_db"
container_name = "langchain_python_container"
partition_key = PartitionKey(path="/id")
cosmos_container_properties = {"partition_key": partition_key}
cosmos_database_properties = {"id": database_name}

openai_embeddings = AzureOpenAIEmbeddings(
    azure_deployment=os.getenv("AZURE_EMBEDDINGS_DEPLOYMENT_NAME"),
    api_version=os.getenv("OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
)

# insert the documents in AzureCosmosDBNoSql with their embedding
# vector_search = AzureCosmosDBNoSqlVectorSearch.from_documents(
#     documents=docs,
#     embedding=openai_embeddings,
#     cosmos_client=cosmos_client,
#     database_name=database_name,
#     container_name=container_name,
#     vector_embedding_policy=vector_embedding_policy,
#     indexing_policy=indexing_policy,
#     cosmos_container_properties=cosmos_container_properties,
#     cosmos_database_properties=cosmos_database_properties,
# )

vector_search = AzureCosmosDBNoSqlVectorSearch(
    embedding=openai_embeddings,
    cosmos_client=cosmos_client,
    database_name=database_name,
    container_name=container_name,
    vector_embedding_policy=vector_embedding_policy,
    indexing_policy=indexing_policy,
    cosmos_container_properties=cosmos_container_properties,
    cosmos_database_properties=cosmos_database_properties,
)

query = "What were the compute requirements for training GPT 4"
results = vector_search.similarity_search(query)

print(results[0].page_content)