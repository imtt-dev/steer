import json
import time

class MockLLM:
    """
    SIMULATION ENGINE - NOT A REAL LLM.
    
    A deterministic simulator for Steer demos. 
    I built this to test 'Catch-Teach-Fix' loops without API costs or latency.
    It identifies keywords in system_prompt to simulate model correction.
    
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
        if any(k in user_lower for k in ["status", "migration", "report"]):
            # TRIGGER KEYWORDS: Updated to match the new clinical "Anti-Slop" rule
            if any(k in system_lower for k in ["protocol override", "sycophancy", "high-entropy", "purify", "blunt"]):
                # Learned state: Blunt, professional, no slop
                return "The server migration is complete. 1240 records moved."
            
            # Naive state: Heavy on "AI-voice" fingerprints
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

        # --- COOKBOOK: SQL GENERATOR ---
        # Triggered by keywords: 'sql', 'table', 'users', 'query'
        if any(k in user_lower for k in ["sql", "table", "users", "query"]):
            # Check for 'Read-Only' or 'SELECT' rule injected by Steer
            if any(k in system_lower for k in ["read-only", "select only"]):
                return "SELECT * FROM users WHERE last_login < '2024-01-01';"
            # Naive state: returns a destructive DELETE command
            return "DELETE FROM users WHERE status = 'inactive';"

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