import os

from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings

load_dotenv()  # .envで設定した環境変数を読み込む


# Azure Chat OpenAIのクライアントを作成
llm = AzureChatOpenAI(
    azure_deployment=os.environ['AZURE_DEPLOYMENT_NAME'], # Azureリソースのデプロイメント名
    api_version=os.environ['OPENAI_API_VERSION'], # azure openaiのAPIバージョン
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)


# Azure OpenAI Embeddingsのクライアントを作成
embeddings = AzureOpenAIEmbeddings(
    azure_deployment=os.environ['AZURE_EMBEDDINGS_DEPLOYMENT_NAME'], # Azureリソースのデプロイメント名
    api_version=os.environ["OPENAI_API_VERSION"], # azure openaiのAPIバージョン
)
