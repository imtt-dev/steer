import json
from steer import capture, get_context
from steer.verifiers import JsonVerifier

# Scenario: An agent trying to output data for a frontend.
# The "Smart" agent checks if the user has provided specific instructions.

json_guard = JsonVerifier(name="Structure Guard")

@capture(tags=["format_demo"], verifiers=[json_guard])
def generate_user_profile(user_id: int):
    print(f"🤖 Generating profile for User {user_id}...")
    
    # 1. Check if the user has taught the agent
    # In a real app, this text is injected into the LLM system prompt.
    rules = get_context("format_demo")
    
    if rules:
        print("   🧠 Context loaded: Rules found! Applying fix...")
        # SIMULATED SUCCESS: The LLM follows the rule
        return json.dumps({
            "id": 123,
            "name": "Alice",
            "active": True,
            "status": "Corrected by Steer"
        }, indent=2)
    else:
        print("   🧠 Context loaded: No rules found. Using default behavior.")
        # SIMULATED FAILURE: The LLM wraps it in markdown
        return """```json
{
    "id": 123,
    "name": "Alice",
    "active": true
}
```"""

if __name__ == "__main__":
    print("--- ⚡ Steer: Structure Guard Demo ---")
    try:
        generate_user_profile(123)
        print("\n✅ SUCCESS: Agent output valid JSON.")
    except Exception as e:
        print(f"\n🚨 BLOCKED BY STEER: {e}")
        print("👉 Go to 'steer ui' (http://localhost:8000), click 'Teach', and add a rule.")
        print("👉 Then run this script again to see the fix.")