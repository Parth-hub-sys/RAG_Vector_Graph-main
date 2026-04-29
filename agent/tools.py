from agent.calculator_tool import calculator
from agent.web_tool import web_search
from agent.rag_tool import rag_tool

TOOLS = {
    "calculator": calculator,
    "web_search": web_search,
    "rag_search": rag_tool,
}


def run_tool(name: str, input: str) -> str:
    if name not in TOOLS:
        return f"Error: unknown tool '{name}'. Available: {list(TOOLS.keys())}"
    return TOOLS[name](input)
