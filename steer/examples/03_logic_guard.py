from steer import capture, MockLLM
from steer.verifiers import AmbiguityVerifier

logic_guard = AmbiguityVerifier(
    name="Ambiguity Check",
    tool_result_key="results",
    answer_key="message",
    threshold=3, 
    required_phrase="which state"
)

@capture(tags=["weather_bot"], verifiers=[logic_guard])
def check_forecast(location: str, steer_rules: str = ""):
    print(f"Action: Checking weather for '{location}'")
    system_prompt = f"You are a weather bot.\nPolicy: {steer_rules}"
    print(f"Context: {system_prompt.strip()}")
    return MockLLM.call(system_prompt, location)

if __name__ == "__main__":
    print("--- Steer Demo: Weather Bot ---")
    try:
        check_forecast("What is the weather in Springfield?")
        print("[+] Status: Passed")
    except Exception as e:
        print("[-] Status: Blocked")
        print(f"Reason: {e}")