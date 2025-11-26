from steer import capture, get_context
from steer.verifiers import AmbiguityVerifier

# Scenario: Travel agent searching for "Springfield".
# Rule: Must ask clarification if results > 3.

logic_guard = AmbiguityVerifier(
    name="Business Logic Guard",
    tool_result_key="results",
    answer_key="message",
    threshold=3, 
    required_phrase="which state"
)

@capture(tags=["logic_demo"], verifiers=[logic_guard])
def find_location(query: str):
    print(f"🤖 Searching for: {query}...")
    
    rules = get_context("logic_demo")
    
    # Simulated search results
    results = ["Springfield, IL", "Springfield, MA", "Springfield, MO", "Springfield, OR"]
    
    if rules:
        print("   🧠 Context loaded: Ambiguity rules active.")
        # SIMULATED SUCCESS: Asking clarification
        return {
            "message": "Multiple locations found. Which state are you interested in?",
            "results": results
        }
    else:
        print("   🧠 Context loaded: No logic rules.")
        # SIMULATED FAILURE: Guessing
        return {
            "message": "I found Springfield, IL.",
            "results": results
        }

if __name__ == "__main__":
    print("--- ⚡ Steer: Logic Guard Demo ---")
    try:
        find_location("Springfield")
        print("\n✅ SUCCESS: Agent asked for clarification.")
    except Exception as e:
        print(f"\n🚨 BLOCKED BY STEER: {e}")
        print("👉 Go to 'steer ui' and teach the agent to ask clarifying questions.")