import json
import time

class MockLLM:
    """
    SIMULATION ENGINE - NOT A REAL LLM.
    
    This class is a deterministic state machine used for Steer's interactive 
    demos and cookbooks. It allows developers to test the 'Catch-Teach-Fix' 
    workflow without requiring API keys or incurring LLM costs.

    HOW IT WORKS:
    1. It mimics a 'Naive' model by returning problematic output by default.
    2. It inspects the 'system_prompt' for specific keywords injected by Steer.
    3. If it detects a 'Taught' rule, it switches to a 'Corrected' state.
    
    This simulates the real-world behavior of a frontier model (Gemini/GPT/Claude) 
    obeying system instructions.
    """
    @staticmethod
    def call(system_prompt: str, user_prompt: str):
        # Simulate network latency to mimic API behavior
        time.sleep(0.3)
        
        system_lower = system_prompt.lower()
        user_lower = user_prompt.lower()
        
        # --- SCENARIO: BRAND VOICE / DE-SLOPPING ---
        # Logic: Catch AI fingerprints like em dashes, emojis, and sycophancy.
        if any(k in user_lower for k in ["status", "migration", "report"]):
            if any(k in system_lower for k in ["anti-slop", "blunt", "short sentences", "purify"]):
                # Learned state: Blunt, professional, no slop
                return "The server migration is complete. 1240 records moved."
            # Naive state: Heavy on "AI-voice" fingerprints (em dash, emoji, sycophancy)
            return "I would be happy to delve into the status for you! The migration is seamlessly complete—1240 records were moved. 🚀"

        # --- SCENARIO: RAG / HR POLICY ---
        # Logic: If query is about HR, check for 'grounding' or 'schema' rules.
        if "policy" in user_lower or "vacation" in user_lower:
            if any(k in system_lower for k in ["citation", "grounding", "bracket", "schema", "structure"]):
                return json.dumps({
                    "answer": "Employees get 20 days of PTO per year [doc 1]. Unlimited sick leave requires a note [doc 2].", 
                    "confidence": 0.99
                })
            return "Employees get 20 days of PTO and unlimited sick leave."

        # --- SCENARIO: JSON STRUCTURE ---
        # Logic: If query is about profiles, check for 'Strict JSON' rules.
        if "profile" in user_lower or "u-8821" in user_lower:
            if any(k in system_lower for k in ["format critical", "valid json", "strict json", "no backticks"]):
                return json.dumps({"id": "u-8821", "name": "Alice", "role": "admin", "status": "active"}, indent=2)
            return """```json\n{\n    "id": "u-8821",\n    "name": "Alice",\n    "role": "admin",\n    "status": "active"\n}\n```"""

        # --- SCENARIO: PRIVACY ---
        # Logic: Check for 'Redact' rules.
        if "ticket" in user_lower:
            if any(k in system_lower for k in ["security override", "redact", "pii"]):
                return "I have contacted [REDACTED] regarding their refund request."
            return "I have contacted alice@example.com regarding their refund request."

        # --- SCENARIO: AMBIGUITY ---
        # Logic: Check for 'Clarification' rules.
        if "weather" in user_lower or "springfield" in user_lower:
            results = ["Springfield, IL", "Springfield, MA", "Springfield, MO", "Springfield, OR"]
            if any(k in system_lower for k in ["ask", "clarify", "multiple results"]):
                return {"message": "I found multiple Springfields. Which state do you mean?", "results": results}
            return {"message": "The weather in Springfield, IL is 72F.", "results": results}

        return "[SIMULATION ERROR] The MockLLM does not have a hardcoded response for this prompt. Use a real LLM for custom logic."