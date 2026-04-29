from langchain_groq import ChatGroq
from retrieval.hybrid_retriever import hybrid_context
from dotenv import load_dotenv
import os
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_llm = None

def _get_llm():
    global _llm
    if _llm is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not set in .env")
        _llm = ChatGroq(api_key=api_key, model="openai/gpt-oss-120b", temperature=0)
    return _llm


def answer(query):
    """Answer the query by summarizing and synthesizing both vector and graph contexts.

    Steps for the LLM:
    1) Produce a short "Document Summary" (2-3 sentences) from Document Context.
    2) Produce a short "Graph Summary" (2-3 sentences) from Knowledge Graph Context.
    3) Synthesize a concise final answer that merges both summaries and cite which sources were used.
    If a context section is missing, explicitly note it and answer from the available source.
    """
    logger.info(f"Processing query: {query}")

    context = hybrid_context(query)

    prompt = f"""
You are a helpful assistant. You will be given CONTEXT and a QUESTION.

CONTEXT may include two labeled sections:
- Document Context: textual excerpts retrieved by vector search
- Knowledge Graph Context: direct relationship lines retrieved by Neo4j (one relation per line)
It will also include a short line indicating which sources were used.

Task:
1) Write a brief "Document Summary" (2-3 sentences). If no Document Context is present, write: "No Document Context available."
2) Under the label "Graph Relations:", list the raw relations exactly as provided in the Knowledge Graph Context (one per line). If no Graph Context is present, write: "No Graph Context available."
3) Write a concise, final answer to the QUESTION that synthesizes the Document Summary and the Graph Relations. Prefer facts present in both sources; if only one source exists, answer from that source and note which source was used.
4) Add a final line "Sources: ..." listing which of VECTOR and/or GRAPH were used.

Output format (exact labels):
Document Summary:
<2-3 sentence paragraph>

Graph Relations:
<one relation per line, or "No Graph Context available.">

Final Answer:
<concise answer>

Sources: VECTOR, GRAPH

CONTEXT:
{context}

QUESTION: {query}

Answer:
"""

    response = _get_llm().invoke(prompt).content
    return response
