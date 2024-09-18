"""様々な媒体からドキュメントを読み込む方法についてまとめたファイル"""

import os
# ユーザーエージェントを設定しないとエラーが出るので設定
os.environ['USER_AGENT'] = "my_user_agent"

from langchain_community.document_loaders import WebBaseLoader
from langchain_community.document_loaders import RecursiveUrlLoader
from langchain_text_splitters import HTMLSectionSplitter

import re
from bs4 import BeautifulSoup



url = "https://kyoto-tech.ac.jp/"


def simple_loader():
    """一つのURLからドキュメントを読み込む"""
    loader = WebBaseLoader(url)
    docs = loader.load()
    print(docs[0])
    return


def bs4_extractor(html: str) -> str:
    """BeautifulSoupを使ってhtmlからテキストを抽出する"""
    soup = BeautifulSoup(html, "lxml")
    return re.sub(r"\n\n+", "\n\n", soup.text).strip()


def recursive_loader():
    """再帰的にドキュメントを読み込む"""
    loader = RecursiveUrlLoader(url, max_depth=1, extractor=bs4_extractor)
    docs = loader.load()
    print(docs[0])
    for doc in docs:
        print(doc.metadata)
    print(len(docs))
    return docs


def html_splitter(docs):
    """htmlを分割する"""
    headers_to_split_on = [("h1", "Header 1"), ("h2", "Header 2")]

    html_splitter = HTMLSectionSplitter(headers_to_split_on)
    html_header_splits = html_splitter.split_documents(docs)
    print(html_header_splits)
    return 



if __name__ == "__main__":
    docs = recursive_loader()
    html_splitter(docs)
