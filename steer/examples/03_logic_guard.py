from steer import capture
from steer.verifiers import AmbiguityVerifier

# Scenario: Travel agent searching for "Springfield".
logic_guard = AmbiguityVerifier(
    name="Business Logic Guard",
    tool_result_key="results",
    answer_key="message",
    threshold=3, 
    required_phrase="which state"
)

@capture(tags=["logic_demo"], verifiers=[logic_guard])
def find_location(query: str, steer_rules: str = ""):
    print(f"🤖 Searching for: {query}...")
    
    results = ["Springfield, IL", "Springfield, MA", "Springfield, MO", "Springfield, OR"]
    
    if steer_rules:
        print(f"   🧠 Context loaded: {steer_rules.strip()}")
        # SIMULATED SUCCESS
        return {"message": "Multiple locations found. Which state are you interested in?", "results": results}
    else:
        print("   🧠 Context loaded: None")
        # SIMULATED FAILURE
        return {"message": "I found Springfield, IL.", "results": results}

if __name__ == "__main__":
    print("--- ⚡ Steer: Logic Guard Demo ---")
    try:
        find_location("Springfield")
        print("\n✅ SUCCESS: Agent asked for clarification.")
    except Exception as e:
        print(f"\n🚨 BLOCKED BY STEER: {e}")
        print("👉 Run 'steer ui' and teach the agent to ask clarifying questions.")