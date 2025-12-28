from steer import capture, MockLLM
from steer.judges import SlopJudge

# The SlopJudge is a deterministic 'Reality Lock' for brand voice.
slop_guard = SlopJudge(name="Slop Filter")

@capture(tags=["brand_voice_agent"], Judges=[slop_guard])
def get_system_status(query: str, steer_rules: str = ""):
    print(f"Action: Generating response for '{query}'")
    
    system_prompt = f"You are a helpful assistant.\n{steer_rules}"
    print(f"Context: {system_prompt.strip()}")

    return MockLLM.call(system_prompt, query)

if __name__ == "__main__":
    print("--- Steer Demo: Slop Guard ---")
    try:
        # This query triggers the MockLLM to return a high-slop response
        get_system_status("Provide a status report on the server migration.")
        print("[+] Status: Passed")
    except Exception as e:
        print("[-] Status: Blocked")
        print(f"Reason: {e}")