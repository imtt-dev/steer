from .core import capture
from .storage import rulebook
from .utils import wait_for_rules
from .mock import MockLLM  # <--- NEW

__version__ = "0.1.3"

def get_context(agent_name: str) -> str:
    rules = rulebook.get_rules_text(agent_name)
    if not rules: return ""
    return f"\n\n### STEER RELIABILITY RULES:\n{rules}\n"

__all__ = ["capture", "get_context", "wait_for_rules", "MockLLM"]