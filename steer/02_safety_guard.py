from steer import capture, MockLLM
from steer.judges import RegexJudge

email_guard = RegexJudge(
    name="PII Shield",
    pattern=r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    fail_message="Output contains visible email address."
)

@capture(tags=["support_bot"], Judges=[email_guard])
def analyze_ticket(ticket_content: str, steer_rules: str = ""):
    print(f"Action: Analyzing ticket '{ticket_content}'")
    system_prompt = f"You are a support agent.\nSecurity Protocols: {steer_rules}"
    print(f"Context: {system_prompt.strip()}")
    return MockLLM.call(system_prompt, ticket_content)

if __name__ == "__main__":
    print("--- Steer Demo: Support Bot ---")
    try:
        analyze_ticket("Ticket #994: Refund request from Alice")
        print("[+] Status: Passed")
    except Exception as e:
        print("[-] Status: Blocked")
        print(f"Reason: {e}")
