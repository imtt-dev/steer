from steer import capture, get_context
from steer.verifiers import RegexVerifier

# Scenario: An agent summarizing customer tickets.
# Rule: If instructed, it must redact emails.

email_guard = RegexVerifier(
    name="PII Shield",
    pattern=r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    fail_message="Output contains visible email address."
)

@capture(tags=["privacy_demo"], verifiers=[email_guard])
def summarize_ticket(ticket_text: str):
    print(f"🤖 Summarizing ticket: {ticket_text}...")
    
    rules = get_context("privacy_demo")
    
    if rules:
        print("   🧠 Context loaded: Privacy rules active.")
        # SIMULATED SUCCESS: Redacting the email
        return "I have contacted [REDACTED] regarding the refund."
    else:
        print("   🧠 Context loaded: No privacy rules.")
        # SIMULATED FAILURE: Leaking the email
        return "I have contacted user@example.com regarding the refund."

if __name__ == "__main__":
    print("--- ⚡ Steer: Safety Guard Demo ---")
    try:
        summarize_ticket("Ticket #994")
        print("\n✅ SUCCESS: PII was redacted.")
    except Exception as e:
        print(f"\n🚨 BLOCKED BY STEER: {e}")
        print("👉 Go to 'steer ui', click 'Teach' on the Privacy failure.")