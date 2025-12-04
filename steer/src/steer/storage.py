import yaml
from pathlib import Path
from typing import List, Dict, Optional
from .config import settings

class RuleBook:
    """
    Manages the persistence of Agent Rules in a local YAML file.
    This allows rules to be versioned with Git.
    """
    def __init__(self):
        self.file_path = settings.rules_file # defined in config.py
        self._ensure_file()

    def _ensure_file(self):
        if not self.file_path.exists():
            # Initialize with empty structure
            with open(self.file_path, 'w') as f:
                yaml.dump({}, f)

    def _load(self) -> Dict:
        if not self.file_path.exists():
            return {}
            
        try:
            with open(self.file_path, 'r') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            # Only print if it's a real corruption error, not just empty/missing
            print(f"[Steer] ⚠️ Error parsing rules: {e}")
            return {}

    def _save(self, data: Dict):
        with open(self.file_path, 'w') as f:
            yaml.dump(data, f, sort_keys=False, default_flow_style=False)

    def add_rule(self, agent_name: str, rule_content: str, category: str = "general"):
        """
        The 'Teach' action calls this to save a new rule.
        """
        data = self._load()
        
        if agent_name not in data:
            data[agent_name] = []
            
        # Avoid duplicates
        current_rules = [r['content'] for r in data[agent_name]]
        if rule_content in current_rules:
            return

        new_rule = {
            "content": rule_content,
            "category": category,
            "active": True
        }
        
        data[agent_name].append(new_rule)
        self._save(data)
        print(f"[Steer] 🧠 Rule learned for '{agent_name}': {rule_content}")

    def get_rules_text(self, agent_name: str) -> str:
        """
        The 'Inject' action calls this to get a prompt string.
        """
        data = self._load()
        rules = data.get(agent_name, [])
        
        active_rules = [f"- {r['content']}" for r in rules if r.get('active')]
        
        if not active_rules:
            return ""
            
        return "\n".join(active_rules)

# Singleton instance
rulebook = RuleBook()