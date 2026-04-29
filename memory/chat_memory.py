from collections import deque

class ChatMemory:
    def __init__(self, max_turns: int = 10):
        self._history = deque(maxlen=max_turns * 2)

    def add(self, role: str, content: str):
        self._history.append({"role": role, "content": content})

    def get_history(self) -> list[dict]:
        return list(self._history)

    def format_for_prompt(self) -> str:
        if not self._history:
            return ""
        lines = [f"{m['role'].upper()}: {m['content']}" for m in self._history]
        return "\n".join(lines)

    def clear(self):
        self._history.clear()


memory = ChatMemory()
