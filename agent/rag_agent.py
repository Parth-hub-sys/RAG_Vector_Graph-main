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


def _format_web_results(results: dict) -> str:
    items = results.get("results", [])
    if not items:
        return "No web results found."
    lines = []
    for item in items[:5]:
        title = item.get("title", "")
        url = item.get("url", "")
        content = item.get("content", "")[:300]
        lines.append(f"- {title} ({url}): {content}")
    return "\n".join(lines)


def answer(query: str, use_web_search: bool = False) -> str:
    logger.info(f"Processing query: {query}, web_search={use_web_search}")

    context = hybrid_context(query)

    web_context_section = ""
    if use_web_search:
        try:
            from agent.web_tool import web_search
            web_results = web_search(query)
            web_text = _format_web_results(web_results)
            web_context_section = f"\n- Web Search Results:\n{web_text}"
            logger.info("Web search results retrieved.")
        except Exception as e:
            logger.warning(f"Web search failed: {e}")
            web_context_section = "\n- Web Search Results:\nWeb search unavailable."

    web_task = (
        "\n4) Under 'Web Search Summary:', summarize key web findings in 2-3 sentences. "
        "If no web results, write 'No Web Context available.'"
        if use_web_search else ""
    )
    web_output_block = (
        "\nWeb Search Summary:\n<2-3 sentence paragraph or 'No Web Context available.'>\n"
        if use_web_search else ""
    )
    web_sources_label = ", WEB" if use_web_search else ""
    web_context_label = (
        '\n- "Web Search Results": live web search results from Tavily'
        if use_web_search else ""
    )

    prompt = f"""You are a helpful assistant. You will be given CONTEXT and a QUESTION.

The CONTEXT contains labeled sections (labels may be prefixed with an emoji):
- "Document Context" or "📄 Document Context (from Vector Search)": textual excerpts from ingested documents
- "Knowledge Graph Context" or "🔗 Knowledge Graph Context (from Graph Database)": entity relationships from Neo4j, each line formatted as "Entity --[RELATION_TYPE]--> Entity" or "• Entity --[RELATION_TYPE]--> Entity"{web_context_label}

Task:
1) Write a "Document Summary" (2-3 sentences) based on the Document Context.
   If the Document Context section is absent or empty, write: "No Document Context available."

2) Under "Graph Relations:", reformat EACH relation from the Knowledge Graph Context into clean, human-readable form:
   - Input format: "Parth Tarsariya --[HAS_SKILL]--> Python"
   - Output format: "Parth Tarsariya → has skill → Python"
   - Rules: lowercase the relation type, replace underscores with spaces, use → arrows
   - List ONE relation per line
   - If the Knowledge Graph Context section is absent or empty, write: "No Graph Context available."{web_task}
3) Write a concise final answer to the QUESTION that synthesizes all available sources.
   If only one source is available, answer from that source and note it.

4) Add "Sources:" line listing which of VECTOR, GRAPH{web_sources_label} were used.

Output (use these exact section labels):
Document Summary:
<2-3 sentence paragraph>

Graph Relations:
<one "A → relation → B" per line, or "No Graph Context available.">
{web_output_block}
Final Answer:
<concise answer>

Sources: VECTOR, GRAPH{web_sources_label}

CONTEXT:
{context}{web_context_section}

QUESTION: {query}

Answer:
"""

    response = _get_llm().invoke(prompt).content
    return response
