from .core import capture
from .storage import rulebook
from .utils import wait_for_rules
from .mock import MockLLM
from .judges import (
    RealityLock, 
    JsonJudge, 
    RegexJudge, 
    SqlJudge, 
    PydanticJudge, 
    CitationJudge, 
    SlopJudge,
    AmbiguityJudge
)

__version__ = "0.3.5"

def get_context(agent_name: str) -> str:
    rules = rulebook.get_rules_text(agent_name)
    if not rules: return ""
    return f"\n\n### STEER RELIABILITY RULES:\n{rules}\n"

def init(config: str = None, patch: list = None):
    # Stub for future platform features, kept to prevent test breakage
    pass

__all__ = [
    "capture", "init", "get_context", "wait_for_rules", "MockLLM", 
    "RealityLock", "JsonJudge", "RegexJudge", "SqlJudge", 
    "PydanticJudge", "CitationJudge", "SlopJudge", "AmbiguityJudge"
]