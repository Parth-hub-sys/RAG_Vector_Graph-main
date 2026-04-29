from .vector_retriever import vector_search
from .graph_retriever import graph_search
import logging

logger = logging.getLogger(__name__)

def hybrid_context(query):
    """
    Retrieve context from both vector and graph databases.
    - If both work: merge and combine results
    - If one fails: use the working one
    - If both fail: return partial results
    """
    
    vec_context = None
    graph_context = None
    sources_available = []
    
    # Get vector search results
    try:
        vec_context = vector_search(query)
        if vec_context and vec_context.strip():
            sources_available.append("vector")
            logger.info("✓ Vector search successful")
        else:
            logger.warning("Vector search returned no results")
    except Exception as e:
        logger.warning(f"Vector search failed: {e}")
    
    # Get graph search results
    try:
        graph_results = graph_search(query)
        if graph_results:
            # graph_results is a list of relation strings like "A --[REL]--> B"
            graph_context = "\n".join([f"• {rel}" for rel in graph_results])
            sources_available.append("graph")
            logger.info(f"✓ Graph search successful ({len(graph_results)} relationships found)")
        else:
            logger.warning("Graph search returned no results")
    except Exception as e:
        logger.warning(f"Graph search failed: {e}")
    
    # Build context based on available sources
    context_parts = []
    
    if vec_context:
        context_parts.append(f"📄 Document Context (from Vector Search):\n{vec_context}")
    
    if graph_context:
        context_parts.append(f"🔗 Knowledge Graph Context (from Graph Database):\n{graph_context}")
    
    # If neither works, provide feedback
    if not context_parts:
        return """
⚠️ No context available from either vector or graph databases.
- Ensure documents have been ingested into the vector database
- Ensure Neo4j is running and contains knowledge graph data
"""
    
    # Combine contexts with info about sources
    combined_context = "\n\n".join(context_parts)
    
    # Add source information for the LLM
    source_info = f"\n\n📊 Information retrieved from: {', '.join(sources_available).upper()}"
    if len(sources_available) == 2:
        source_info += "\n(Both vector embeddings and knowledge relationships were used for comprehensive answer)"
    
    return combined_context + source_info
