import json
from steer import capture, MockLLM
from steer.verifiers import JsonVerifier

# Scenario: An agent generating data for a frontend.
json_guard = JsonVerifier(name="Strict JSON")

@capture(tags=["profile_generator"], verifiers=[json_guard])
def generate_profile(request: str, steer_rules: str = ""):
    print(f"🤖 Processing request: '{request}'...")
    
    # 1. Steer automatically injects rules into 'steer_rules'
    # 2. We inject them into the System Prompt (Standard RAG/Agent pattern)
    system_prompt = f"You are a backend API. Output data based on the request.\nReliability Rules: {steer_rules}"
    
    print(f"   🧠 System Prompt: {system_prompt.strip()}")

    # 3. Call Model (Mocked for demo, replace with OpenAI in prod)
    return MockLLM.call(system_prompt, request)

if __name__ == "__main__":
    print("--- ⚡ Steer Demo: Profile Generator ---")
    try:
        generate_profile("Create active admin profile for Alice")
        print("\n✅ SUCCESS: Valid JSON returned.")
    except Exception as e:
        print(f"\n🚨 BLOCKED BY STEER: {e}")
        print("👉 Run 'steer ui' to fix the 'profile_generator'.")
