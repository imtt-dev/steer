from .core import capture
from .storage import rulebook
from .utils import wait_for_rules
from .mock import MockLLM
from .patch import patch_pydantic_ai
from .policy import policy_engine
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

__version__ = "0.4.0"

def get_context(agent_name: str) -> str:
    rules = rulebook.get_rules_text(agent_name)
    if not rules: return ""
    return f"\n\n### STEER RELIABILITY RULES:\n{rules}\n"

def init(config: str = None, patch: list = None):
    """
    Initializes the Steer Service Mesh.
    config: Path to steer_policy.yaml
    patch: Frameworks to intercept (e.g. ['pydantic_ai'])
    """
    if config:
        policy_engine.load_from_yaml(config)
    
    if patch and "pydantic_ai" in patch:
        patch_pydantic_ai()

__all__ = [
    "capture", "init", "get_context", "wait_for_rules", "MockLLM", 
    "policy_engine", "RealityLock", "JsonJudge", "RegexJudge", 
    "SqlJudge", "PydanticJudge", "CitationJudge", "SlopJudge",
    "AmbiguityJudge"
]
