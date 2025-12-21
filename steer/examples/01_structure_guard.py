import json
from steer import capture, MockLLM
from steer.verifiers import JsonVerifier

json_guard = JsonVerifier(name="Strict JSON")

@capture(tags=["profile_generator"], verifiers=[json_guard])
def generate_profile(request: str, steer_rules: str = ""):
    print(f"Action: Processing request '{request}'")
    system_prompt = f"You are a backend API. Output data based on the request.\nReliability Rules: {steer_rules}"
    print(f"Context: {system_prompt.strip()}")
    return MockLLM.call(system_prompt, request)

if __name__ == "__main__":
    print("--- Steer Demo: Profile Generator ---")
    try:
        generate_profile("Create active admin profile for Alice")
        print("[+] Status: Passed")
    except Exception as e:
        print("[-] Status: Blocked")
        print(f"Reason: {e}")