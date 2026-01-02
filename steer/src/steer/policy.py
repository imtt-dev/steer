import yaml
from pathlib import Path
from typing import Dict, List, Optional
from .judges import (
    RealityLock, JsonJudge, SqlJudge, 
    PydanticJudge, CitationJudge, SlopJudge
)

class PolicyRegistry:
    def __init__(self):
        self._agent_map: Dict[str, List[RealityLock]] = {}
        self._global_locks: List[RealityLock] = []

    def load_from_yaml(self, path: str):
        p = Path(path)
        if not p.exists():
            return
            
        try:
            with open(p, "r") as f:
                data = yaml.safe_load(f) or {}
            
            if "global" in data:
                self._global_locks = self._parse_lock_list(data["global"])
                
            if "agents" in data:
                for agent_name, lock_names in data["agents"].items():
                    self._agent_map[agent_name] = self._parse_lock_list(lock_names)
        except Exception:
            pass

    def _parse_lock_list(self, names: List[str]) -> List[RealityLock]:
        lookup = {
            "SqlJudge": SqlJudge,
            "SlopJudge": SlopJudge,
            "JsonJudge": JsonJudge,
            "CitationJudge": CitationJudge
        }
        return [lookup[n]() for n in names if n in lookup]

    def get_locks_for_agent(self, agent_name: str, discovered_locks: Optional[List[RealityLock]] = None) -> List[RealityLock]:
        explicit = self._agent_map.get(agent_name, [])
        all_locks = self._global_locks + explicit + (discovered_locks or [])
        seen_types = set()
        unique_locks = []
        for lock in all_locks:
            if type(lock) not in seen_types:
                unique_locks.append(lock)
                seen_types.add(type(lock))
        return unique_locks

policy_engine = PolicyRegistry()
