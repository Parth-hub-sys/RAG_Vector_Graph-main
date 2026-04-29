import pytest
from unittest.mock import patch


def test_hybrid_uses_both_sources():
    with patch("retrieval.hybrid_retriever.vector_search", return_value="vector result"), \
         patch("retrieval.hybrid_retriever.graph_search", return_value=["A --[REL]--> B"]):
        from retrieval.hybrid_retriever import hybrid_context
        result = hybrid_context("test query")
        assert "vector result" in result
        assert "A --[REL]--> B" in result


def test_hybrid_vector_only_when_graph_fails():
    with patch("retrieval.hybrid_retriever.vector_search", return_value="only vector"), \
         patch("retrieval.hybrid_retriever.graph_search", side_effect=Exception("Neo4j down")):
        from retrieval.hybrid_retriever import hybrid_context
        result = hybrid_context("test query")
        assert "only vector" in result


def test_hybrid_graph_only_when_vector_fails():
    with patch("retrieval.hybrid_retriever.vector_search", side_effect=Exception("Chroma down")), \
         patch("retrieval.hybrid_retriever.graph_search", return_value=["X --[Y]--> Z"]):
        from retrieval.hybrid_retriever import hybrid_context
        result = hybrid_context("test query")
        assert "X --[Y]--> Z" in result


def test_hybrid_no_context_message():
    with patch("retrieval.hybrid_retriever.vector_search", return_value=""), \
         patch("retrieval.hybrid_retriever.graph_search", return_value=[]):
        from retrieval.hybrid_retriever import hybrid_context
        result = hybrid_context("test query")
        assert "No context" in result or "no context" in result.lower() or "⚠️" in result


def test_hybrid_empty_query():
    with patch("retrieval.hybrid_retriever.vector_search", return_value=""), \
         patch("retrieval.hybrid_retriever.graph_search", return_value=[]):
        from retrieval.hybrid_retriever import hybrid_context
        result = hybrid_context("")
        assert isinstance(result, str)
