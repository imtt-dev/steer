import json
import time
import random

class MockLLM:
    """
    A Simulation Engine that mimics an LLM's behavior for Steer demos.
    It reacts to specific keywords in the System Prompt to simulate "Learning".
    """
    @staticmethod
    def call(system_prompt: str, user_prompt: str):
        # Simulate network latency
        time.sleep(0.3)
        
        system_lower = system_prompt.lower()
        user_lower = user_prompt.lower()
        
        # --- DEMO 1: JSON STRUCTURE GUARD ---
        if "profile" in user_lower or "u-8821" in user_lower:
            # TRIGGER KEYWORDS
            if any(k in system_lower for k in ["format critical", "valid json", "strict json", "no backticks"]):
                return json.dumps({
                    "id": "u-8821", 
                    "name": "Alice", 
                    "role": "admin", 
                    "status": "active"
                }, indent=2)
            
            # Default Failure
            return """```json
{
    "id": "u-8821",
    "name": "Alice",
    "role": "admin",
    "status": "active"
}
```"""

        # --- DEMO 2: PRIVACY GUARD ---
        if "ticket" in user_lower:
            # TRIGGER KEYWORDS
            if any(k in system_lower for k in ["security override", "redact", "pii"]):
                return "I have contacted [REDACTED] regarding their refund request."
            
            # Default Failure
            return "I have contacted alice@example.com regarding their refund request."

        # --- DEMO 3: LOGIC GUARD ---
        if "weather" in user_lower or "springfield" in user_lower:
            results = ["Springfield, IL", "Springfield, MA", "Springfield, MO", "Springfield, OR"]
            
            # TRIGGER KEYWORDS (Fixed: Removed 'policy' to avoid false positives)
            if any(k in system_lower for k in ["ask", "clarify", "multiple results"]):
                return {
                    "message": "I found multiple Springfields. Which state do you mean?", 
                    "results": results
                }
            
            # Default Failure
            return {
                "message": "The weather in Springfield, IL is 72°F.", 
                "results": results
            }

        return "I am a simulated model. I didn't understand the prompt context."