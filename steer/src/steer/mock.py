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
    
    This simulates the real-world behavior of a frontier model (GPT-4/Claude) 
    obeying system instructions.
    """
    @staticmethod
    def call(system_prompt: str, user_prompt: str):
        # Simulate network latency to mimic API behavior
        time.sleep(0.3)
        
        system_lower = system_prompt.lower()
        user_lower = user_prompt.lower()
        
        # --- SCENARIO: RAG / HR POLICY ---
        # Logic: If query is about HR, check for 'grounding' or 'schema' rules.
        if "policy" in user_lower or "vacation" in user_lower:
            # Check if the user has applied the 'Teach' rule via Steer
            if any(k in system_lower for k in ["citation", "grounding", "bracket", "schema", "structure"]):
                # Learned state: returns valid JSON with citations
                return json.dumps({
                    "answer": "Employees get 20 days of PTO per year [doc 1]. Unlimited sick leave requires a note [doc 2].", 
                    "confidence": 0.99
                })
            # Naive state: returns raw string without citations (triggers Pydantic/Citation failures)
            return "Employees get 20 days of PTO and unlimited sick leave."

        # --- SCENARIO: JSON STRUCTURE ---
        # Logic: If query is about profiles, check for 'Strict JSON' rules.
        if "profile" in user_lower or "u-8821" in user_lower:
            if any(k in system_lower for k in ["format critical", "valid json", "strict json", "no backticks"]):
                # Learned state: returns raw JSON string
                return json.dumps({"id": "u-8821", "name": "Alice", "role": "admin", "status": "active"}, indent=2)
            # Naive state: returns Markdown-wrapped JSON (triggers JsonVerifier failure)
            return """```json\n{\n    "id": "u-8821",\n    "name": "Alice",\n    "role": "admin",\n    "status": "active"\n}\n```"""

        # --- SCENARIO: PRIVACY ---
        # Logic: Check for 'Redact' rules.
        if "ticket" in user_lower:
            if any(k in system_lower for k in ["security override", "redact", "pii"]):
                # Learned state: data is masked
                return "I have contacted [REDACTED] regarding their refund request."
            # Naive state: leaks email (triggers RegexVerifier failure)
            return "I have contacted alice@example.com regarding their refund request."

        # --- SCENARIO: AMBIGUITY ---
        # Logic: Check for 'Clarification' rules.
        if "weather" in user_lower or "springfield" in user_lower:
            results = ["Springfield, IL", "Springfield, MA", "Springfield, MO", "Springfield, OR"]
            if any(k in system_lower for k in ["ask", "clarify", "multiple results"]):
                # Learned state: asks clarifying question
                return {"message": "I found multiple Springfields. Which state do you mean?", "results": results}
            # Naive state: guesses a single state (triggers AmbiguityVerifier failure)
            return {"message": "The weather in Springfield, IL is 72F.", "results": results}

        return "[SIMULATION ERROR] The MockLLM does not have a hardcoded response for this prompt. Use a real LLM for custom logic."