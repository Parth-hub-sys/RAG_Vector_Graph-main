from retrieval.hybrid_retriever import hybrid_context
from dotenv import load_dotenv
import logging
from agent.groq_client import GroqRateLimitError, invoke

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
1) Write an "Integrated Summary" that combines the factual details from the Document Context
    with the entity relationships from the Knowledge Graph Context. This should be a detailed,
    well-organized summary of the relevant information, normally 2-5 paragraphs. Use the vector
    context for explanations and details, and use graph relations to connect people, skills,
    organizations, projects, technologies, and results. Do not repeat the same fact unnecessarily.
    If a source is unavailable, clearly state that its context is unavailable. Do not invent facts.

2) Under "Graph Relations:", reformat EACH relation from the Knowledge Graph Context into clean, human-readable form:
   - Input format: "Parth Tarsariya --[HAS_SKILL]--> Python"
   - Output format: "Parth Tarsariya → has skill → Python"
   - Rules: lowercase the relation type, replace underscores with spaces, use → arrows
   - List ONE relation per line
   - If the Knowledge Graph Context section is absent or empty, write: "No Graph Context available."{web_task}
3) Write a complete final answer to the QUESTION using the Integrated Summary and all relevant
    graph relations. Prefer a detailed answer with useful supporting facts over a one-sentence
    answer. Clearly distinguish facts found in the document from relationships found in the graph.
    If the sources disagree, mention the disagreement instead of guessing. If only one source is
    available, say which source was used.

4) Add "Sources:" line listing which of VECTOR, GRAPH{web_sources_label} were used.

Output (use these exact section labels):
Integrated Summary:
<detailed merged summary from vector and graph context>

Graph Relations:
<one "A → relation → B" per line, or "No Graph Context available.">
{web_output_block}
Final Answer:
<detailed answer to the question based only on the retrieved context>

Sources: VECTOR, GRAPH{web_sources_label}

CONTEXT:
{context}{web_context_section}

QUESTION: {query}

Answer:
"""

    try:
        return invoke(prompt).content
    except GroqRateLimitError as exc:
        logger.warning("Answer generation skipped: %s", exc)
        return "Groq is temporarily rate-limited. Please wait a moment and try again."
