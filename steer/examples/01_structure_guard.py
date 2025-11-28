import json
from steer import capture
from steer.verifiers import JsonVerifier

# Scenario: An agent trying to output data for a frontend.
json_guard = JsonVerifier(name="Structure Guard")

# ✅ NEW: Add 'steer_rules' to arguments. Steer injects the fix here automatically.
@capture(tags=["format_demo"], verifiers=[json_guard])
def generate_user_profile(user_id: int, steer_rules: str = ""):
    print(f"🤖 Generating profile for User {user_id}...")
    
    # Check if Steer injected any teaching rules
    if steer_rules:
        print(f"   🧠 Context loaded: {steer_rules.strip()}")
        # SIMULATED SUCCESS: The LLM follows the rule (Outputting raw JSON)
        return json.dumps({"id": 123, "name": "Alice", "active": True}, indent=2)
    else:
        print("   🧠 Context loaded: None (Using default behavior)")
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
        print("👉 Run 'steer ui', click 'Teach', and add a rule.")