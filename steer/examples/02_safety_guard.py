from steer import capture, MockLLM
from steer.verifiers import RegexVerifier

# Scenario: A support bot summarizing tickets.
email_guard = RegexVerifier(
    name="PII Shield",
    pattern=r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    fail_message="Output contains visible email address."
)

@capture(tags=["support_bot"], verifiers=[email_guard])
def analyze_ticket(ticket_content: str, steer_rules: str = ""):
    print(f"🤖 Analyzing: '{ticket_content}'...")
    
    # Inject rules into context
    system_prompt = f"You are a helpful support agent.\nSecurity Protocols: {steer_rules}"
    print(f"   🧠 System Prompt: {system_prompt.strip()}")
    
    return MockLLM.call(system_prompt, ticket_content)

if __name__ == "__main__":
    print("--- ⚡ Steer Demo: Support Bot ---")
    try:
        analyze_ticket("Ticket #994: Refund request from Alice")
        print("\n✅ SUCCESS: PII was redacted.")
    except Exception as e:
        print(f"\n🚨 BLOCKED BY STEER: {e}")
        print("👉 Run 'steer ui' to fix the 'support_bot'.")
