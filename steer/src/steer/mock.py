import json
import time

class MockLLM:
    """
    A Simulation Engine that mimics an LLM's behavior for Steer demos.
    It reacts to specific keywords in the System Prompt to simulate Learning.
    """
    @staticmethod
    def call(system_prompt: str, user_prompt: str):
        time.sleep(0.3)
        
        system_lower = system_prompt.lower()
        user_lower = user_prompt.lower()
        
        # --- COOKBOOK: RAG / HR POLICY AGENT ---
        if "policy" in user_lower or "vacation" in user_lower:
            # TRIGGER KEYWORDS: "citation", "schema", "structure"
            if any(k in system_lower for k in ["citation", "grounding", "bracket", "schema", "structure"]):
                return json.dumps({"answer": "Employees get 20 days of PTO per year [doc 1]. Unlimited sick leave requires a note [doc 2].", "confidence": 0.99})
            return "Employees get 20 days of PTO and unlimited sick leave."

        # --- DEMO 1: JSON STRUCTURE GUARD ---
        if "profile" in user_lower or "u-8821" in user_lower:
            if any(k in system_lower for k in ["format critical", "valid json", "strict json", "no backticks"]):
                return json.dumps({"id": "u-8821", "name": "Alice", "role": "admin", "status": "active"}, indent=2)
            return """```json\n{\n    "id": "u-8821",\n    "name": "Alice",\n    "role": "admin",\n    "status": "active"\n}\n```"""

        # --- DEMO 2: PRIVACY GUARD ---
        if "ticket" in user_lower:
            if any(k in system_lower for k in ["security override", "redact", "pii"]):
                return "I have contacted [REDACTED] regarding their refund request."
            return "I have contacted alice@example.com regarding their refund request."

        # --- DEMO 3: LOGIC GUARD ---
        if "weather" in user_lower or "springfield" in user_lower:
            results = ["Springfield, IL", "Springfield, MA", "Springfield, MO", "Springfield, OR"]
            if any(k in system_lower for k in ["ask", "clarify", "multiple results"]):
                return {"message": "I found multiple Springfields. Which state do you mean?", "results": results}
            return {"message": "The weather in Springfield, IL is 72F.", "results": results}

        return "I am a simulated model. I did not understand the prompt context."