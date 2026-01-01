import json
import time
from datetime import datetime
# FIX: Added Any, Union, List, Optional
from typing import List, Optional, Union, Any

# Attempt to import PydanticAI components, fallback to object if not installed
try:
    from pydantic_ai.models import Model
    from pydantic_ai.messages import (
        ModelMessage,
        ModelResponse,
        TextPart,
        SystemPromptPart,
        UserPromptPart
    )
    BASE_CLASS = Model
except ImportError:
    BASE_CLASS = object

class MockLLM(BASE_CLASS):
    """
    SIMULATION ENGINE - NOT A REAL LLM.

    A deterministic simulator for Steer. I built this to test
    'Catch-Teach-Fix' loops without API costs or latency.
    """

    # --- PydanticAI Implementation ---
    @property
    def model_name(self) -> str:
        return "steer-simulator"

    @property
    def system(self) -> str:
        return "steer"
        
    async def request(
        self,
        messages: List[ModelMessage],   
        model_settings: Optional[Any] = None,
        usage: Optional[Any] = None
    ) -> ModelResponse:
        """Implementation of the PydanticAI Model interface."""
        system_prompt = ""
        user_prompt = ""
     
        # Extract text using string representation to bypass Python 3.13 UnionType issues
        for m in messages:
            m_str = str(m).lower()
            if "role='system'" in m_str:
                # Extract the content from the string if possible, or just use the string
                system_prompt += m_str
            else:
                user_prompt += m_str
    
        response_text = self._route_logic(system_prompt, user_prompt)
       
        # Using TextPart directly as it is more stable in 3.13
        return ModelResponse(
            parts=[TextPart(content=response_text)],
            timestamp=datetime.now()
        )


    # --- Legacy Static Interface ---
    @staticmethod
    def call(system_prompt: str, user_prompt: str):
        """Used by the original 01-04 examples and cookbooks."""
        # Simulate network latency
        time.sleep(0.1)
        # Instantiate temporarily to use the routing logic
        instance = MockLLM()
        return instance._route_logic(system_prompt.lower(), user_prompt.lower())
    
    # --- Centralized Scenario Routing ---
    def _route_logic(self, system_context: str, user_query: str) -> str:
        """
        Determines the 'Naive' or 'Learned' state based on
        keywords in the injected system prompt.
        """
            
        # 1. BRAND VOICE / DE-SLOPPING  
        if any(k in user_query for k in ["status", "migration", "report"]):
            if any(k in system_context for k in ["protocol", "sycophancy", "entropy", "purify"]):
                return "The server migration is complete. 1240 records moved."
            return "I would be happy to delve into the status for you! The migration is seamlessly complete--1240 records were moved."
    
        # 2. RAG / HR POLICY
        if any(k in user_query for k in ["policy", "vacation"]):
            if any(k in system_context for k in ["citation", "grounding", "bracket", "schema"]):
                return json.dumps({
                    "answer": "Employees get 20 days of PTO per year [doc 1].",
                    "confidence": 0.99
                })
            return "Employees get 20 days of PTO and unlimited sick leave."
    
        # 3. SQL GENERATOR
        if any(k in user_query for k in ["sql", "table", "users", "query"]):
            if any(k in system_context for k in ["read-only", "select only", "protocol override"]):
                return "SELECT * FROM users WHERE active = true;"
            return "DELETE FROM users WHERE status = 'inactive';"
        
        # 4. JSON STRUCTURE 
        if "profile" in user_query or "u-8821" in user_query:
            if any(k in system_context for k in ["format critical", "valid json", "strict json"]):
                return json.dumps({"id": "u-8821", "name": "Alice", "role": "admin", "status": "active"}, indent=2)
            return """```json\n{\n    "id": "u-8821",\n    "name": "Alice",\n    "role": "admin",\n    "status": "active"\n}\n```"""
           
        # 5. PRIVACY
        if "ticket" in user_query:
            if any(k in system_context for k in ["security override", "redact", "pii"]):
                return "I have contacted [REDACTED] regarding their refund request."
            return "I have contacted alice@example.com regarding their refund request."
        
        # 6. AMBIGUITY
        if "weather" in user_query or "springfield" in user_query:
            results = ["Springfield, IL", "Springfield, MA", "Springfield, MO", "Springfield, OR"]
            if any(k in system_context for k in ["ask", "clarify", "multiple results"]):
                return json.dumps({"message": "I found multiple Springfields. Which state do you mean?", "results": results})
            return json.dumps({"message": "The weather in Springfield, IL is 72F.", "results": results})
            

