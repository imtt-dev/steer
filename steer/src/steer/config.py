import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class SteerConfig:
    def __init__(self):
        self.project_root = Path(os.getcwd())
        self.steer_dir = self.project_root / ".steer"
        self.log_file = self.steer_dir / "runs.jsonl"
        self.rules_file = self.project_root / "steer_rules.yaml"
        self.steer_dir.mkdir(parents=True, exist_ok=True)

        # Keys
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY") # <--- NEW
        
        # Judge Defaults
        self.judge_model = os.getenv("Steer_JUDGE_MODEL", "gemini/gemini-1.5-flash")

settings = SteerConfig()