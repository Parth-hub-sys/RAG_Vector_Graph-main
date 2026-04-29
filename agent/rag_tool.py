from retrieval.hybrid_retriever import hybrid_context

def rag_tool(query: str):
    return hybrid_context(query)
