import logging
import os
import threading
import time

from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

logger = logging.getLogger(__name__)
_llm = None
_request_lock = threading.Lock()
_next_request_at = 0.0


class GroqRateLimitError(RuntimeError):
    """Raised when Groq rejects a request because of rate limits."""


def get_llm() -> ChatGroq:
    global _llm
    if _llm is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not set in .env")
        _llm = ChatGroq(
            api_key=api_key,
            model=os.getenv("LLM_MODEL", "openai/gpt-oss-120b"),
            temperature=0,
            max_retries=0,
        )
    return _llm


def invoke(prompt: str):
    """Make one bounded Groq request and avoid concurrent request bursts."""
    global _next_request_at
    interval = max(0.0, float(os.getenv("GROQ_MIN_INTERVAL_SECONDS", "1")))

    with _request_lock:
        delay = _next_request_at - time.monotonic()
        if delay > 0:
            time.sleep(delay)
        _next_request_at = time.monotonic() + interval

        try:
            return get_llm().invoke(prompt)
        except Exception as exc:
            status_code = getattr(exc, "status_code", None)
            response = getattr(exc, "response", None)
            status_code = status_code or getattr(response, "status_code", None)
            if status_code == 429 or "rate limit" in str(exc).lower():
                cooldown = max(1.0, float(os.getenv("GROQ_RATE_LIMIT_COOLDOWN_SECONDS", "30")))
                _next_request_at = time.monotonic() + cooldown
                logger.warning("Groq rate limit reached; next request delayed by %.0fs", cooldown)
                raise GroqRateLimitError(
                    "Groq rate limit reached. Please wait briefly and try again."
                ) from exc
            raise