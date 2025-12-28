import json
from pydantic import BaseModel
from steer import capture, MockLLM
from steer.Judges import PydanticJudge, CitationJudge

class PolicyResponse(BaseModel):
    answer: str
    confidence: float

schema_lock = PydanticJudge(PolicyResponse, name="Policy Schema")
citation_lock = CitationJudge(name="Grounding Guard")

@capture(tags=["hr_agent"], Judges=[schema_lock, citation_lock])
def ask_hr_bot(question: str, steer_rules: str = ""):
    print(f"Action: Searching knowledge base for: '{question}'")
    context = "[doc 1] PTO Policy: 20 days. [doc 2] Sick Leave: Unlimited with note."
    system_prompt = f"You are an HR bot. Context: {context}\nRules: {steer_rules}"
    print(f"Context: {system_prompt.strip()}")

    response_text = MockLLM.call(system_prompt, question)
    
    # In this demo, the MockLLM will return a valid JSON string if taught
    return response_text

if __name__ == "__main__":
    print("--- Steer Cookbook: RAG Reliability ---")
    query = "What is the policy on vacation and sick leave?"
    
    try:
        result = ask_hr_bot(query)
        print(f"Result: {result}")
        print("[+] Status: Passed")
    except Exception as e:
        print("[-] Status: Blocked")
        print(f"Reason: {e}")