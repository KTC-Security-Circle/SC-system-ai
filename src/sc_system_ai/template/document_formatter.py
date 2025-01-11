import re
from datetime import datetime
from typing import Any

from langchain_core.documents import Document
from langchain_text_splitters import (
    CharacterTextSplitter,
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

def _max_level(text: str) -> int:
    """Markdownのヘッダーの最大レベルを返す関数"""
    headers = re.findall(r"^#+", text, re.MULTILINE)
    return max([len(h) for h in headers]) if headers else 0

def markdown_splitter(
    text: str,
) -> list[Document]:
    """Markdownをヘッダーで分割する関数"""
    headers_to_split_on = [
        ("#" * (i + 1), f"Header {i + 1}")
        for i in range(_max_level(text))
    ]
    splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on,
        return_each_line=True,
    )
    return splitter.split_text(text)

def _find_header(document: Document) -> str | None:
    """ドキュメントのヘッダー名を返す関数"""
    i = 0
    while True:
        if document.metadata.get(f"Header {i + 1}") is None:
            break
        i += 1
    return document.metadata[f"Header {i}"] if i != 0 else None

def recursive_document_splitter(
    documents: list[Document],
    chunk_size: int,
    chunk_overlap: int,
) -> list[Document]:
    """再帰的に分割する関数"""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    return splitter.split_documents(documents)

def document_splitter(
        documents: Document | list[Document],
        separator: str = "\n\n",
        chunk_size: int = CHUNK_SIZE,
        chunk_overlap: int = CHUNK_OVERLAP,
    ) -> list[Document]:
    """Documentを分割する関数"""
    _documents = documents if isinstance(documents, list) else [documents]
    splitter = CharacterTextSplitter(
        separator=separator,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    return splitter.split_documents(_documents)

def character_splitter(
        text: str,
        separator: str = "\n\n",
        chunk_size: int = CHUNK_SIZE,
        chunk_overlap: int = CHUNK_OVERLAP,
    ) -> list[Document]:
    """文字列を分割する関数"""
    character_splitter = CharacterTextSplitter(
        separator=separator,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    splitted_text = character_splitter.split_text(text)
    return character_splitter.create_documents(splitted_text)

def add_metadata(
    documents: list[Document],
    title: str,
    source: str | None = None,
    with_timestamp: bool = True,
    with_section_number: bool = False,
    **kwargs: Any
) -> list[Document]:
    """メタデータを追加する関数
    Args:
        documents (list[Document]): ドキュメントのリスト
        title (str): タイトル
        source (str, optional): ソース.
        with_timestamp (bool, optional): タイムスタンプの有無. Defaults to True.
        with_section_number (bool, optional): セクション番号の有無. Defaults to False.
        **kwargs: その他のメタデータ.
    """
    i = 1
    date = datetime.now().strftime("%Y-%m-%d")
    for doc in documents:
        doc.metadata["title"] = title

        if source is not None and \
            doc.metadata.get("source") is None:
            doc.metadata["source"] = source

        if with_timestamp and \
            doc.metadata.get("created_at") is None:
            doc.metadata["created_at"] = date
            doc.metadata["updated_at"] = date

        if with_section_number and \
            doc.metadata.get("section_number") is None:
            doc.metadata["section_number"] = i
            i += 1

        for key, value in kwargs.items():
            doc.metadata[key] = value

    return documents

def md_formatter(
    text: str,
    title: str | None = None,
    metadata: dict[str, Any] | None = None,
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> list[Document]:
    """Markdown形式のテキストをフォーマットする関数
    Args:
        text (str): Markdown形式のテキスト
        title (str, optional): タイトル.
        metadata (dict[str, Any], optional): メタデータ.
        chunk_size (int, optional): 分割するサイズ.
        chunk_overlap (int, optional): オーバーラップのサイズ.

    chunk_sizeを超えるテキストは再分割し、メタデータにセクション番号を付与します.
    """
    formatted_docs: list[Document] = []
    _metadata = metadata if metadata is not None else {}

    for doc in markdown_splitter(text):
        t = _find_header(doc) if title is None else title
        if len(doc.page_content) > chunk_size:
            rdocs = recursive_document_splitter(
                [doc],
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
            )
            formatted_docs += add_metadata(
                rdocs,
                title=t if t is not None else rdocs[0].page_content,
                with_section_number=True,
                **_metadata
            )
        else:
            formatted_docs += add_metadata(
                [doc],
                title=t if t is not None else doc.page_content,
                **_metadata
            )

    return formatted_docs

def text_formatter(
    text: str,
    separator: str = "\n\n",
    title: str | None = None,
    metadata: dict[str, Any] | None = None,
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> list[Document]:
    """テキストをフォーマットする関数
    Args:
        text (str): テキスト
        title (str, optional): タイトル.
        metadata (dict[str, Any], optional): メタデータ.
        separator (str, optional): 区切り文字.
        chunk_size (int, optional): 分割するサイズ.
        chunk_overlap (int, optional): オーバーラップのサイズ.

    セパレータとチャンクサイズでテキストを分割し、メタデータにセクション番号を付与します.
    """
    docs = character_splitter(
        text,
        separator=separator,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    return add_metadata(
        docs,
        title=docs[0].page_content if title is None else title,
        with_section_number=True if len(docs) > 1 else False,
        **metadata if metadata is not None else {},
    )

if __name__ == "__main__":
    md_text = """
# Sample Markdown
This is a sample markdown text.


## piyo
There is section 2.
### fuga
but, there is section 3.


## Are you ...?
Are you hogehoge?


### negative answer
No, I'm fugafuga.


### positive answer
Yes, I'm hogehoge.
"""
    def print_docs(docs: list[Document]) -> None:
        for doc in docs:
            print(doc.page_content)
            print(doc.metadata)
            print()


    docs = md_formatter(md_text, title="hogehogehoge", metadata={"fuga": "piyopiyo"})
    print_docs(docs)

    docs = text_formatter(md_text, title="hogehogehoge", metadata={"fuga": "piyopiyo"})
    print_docs(docs)
