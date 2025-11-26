from .core import capture
from .storage import rulebook
from .utils import wait_for_rules # <--- Export this

__version__ = "0.2.0"

def get_context(agent_name: str) -> str:
    rules = rulebook.get_rules_text(agent_name)
    if not rules: return ""
    return f"\n\n### Steer RELIABILITY RULES:\n{rules}\n"

__all__ = ["capture", "get_context", "wait_for_rules"]