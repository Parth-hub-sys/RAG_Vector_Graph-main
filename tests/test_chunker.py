import pytest
from langchain_core.documents import Document
from ingestion.chunker import chunk_documents


def _make_docs(texts: list[str]) -> list[Document]:
    return [Document(page_content=t) for t in texts]


def test_chunks_produced():
    docs = _make_docs(["word " * 200])
    chunks = chunk_documents(docs)
    assert len(chunks) > 1

def test_chunk_size_respected():
    docs = _make_docs(["word " * 500])
    chunks = chunk_documents(docs)
    for chunk in chunks:
        assert len(chunk.page_content) <= 600  # chunk_size + small buffer

def test_short_doc_single_chunk():
    docs = _make_docs(["short text"])
    chunks = chunk_documents(docs)
    assert len(chunks) == 1
    assert chunks[0].page_content == "short text"

def test_empty_doc():
    docs = _make_docs([""])
    chunks = chunk_documents(docs)
    assert isinstance(chunks, list)

def test_multiple_docs():
    docs = _make_docs(["word " * 200, "text " * 200])
    chunks = chunk_documents(docs)
    assert len(chunks) >= 2
