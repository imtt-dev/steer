import sys
import uvicorn
import webbrowser
import argparse
import os
from rich.console import Console
from steer.server import app


DEMO_1_CONTENT = """import json
from steer import capture
from steer.verifiers import JsonVerifier

# Scenario: An agent trying to output data for a frontend.
json_guard = JsonVerifier(name="Structure Guard")

# ✅ NEW: Just add 'steer_rules' argument. Steer auto-populates it.
@capture(tags=["format_demo"], verifiers=[json_guard])
def generate_user_profile(user_id: int, steer_rules: str = ""):
    print(f"🤖 Generating profile for User {user_id}...")
    
    # Check if we have been taught anything
    if steer_rules:
        print(f"   🧠 Context loaded: {steer_rules.strip()}")
        # SIMULATED SUCCESS
        return json.dumps({"id": 123, "name": "Alice", "active": True}, indent=2)
    else:
        print("   🧠 Context loaded: None (Using default behavior)")
        # SIMULATED FAILURE
        return \"\"\"```json
{
    "id": 123,
    "name": "Alice",
    "active": true
}
```\"\"\"

if __name__ == "__main__":
    print("--- ⚡ Steer: Structure Guard Demo ---")
    try:
        generate_user_profile(123)
        print("\\n✅ SUCCESS: Agent output valid JSON.")
    except Exception as e:
        print(f"\\n🚨 BLOCKED BY STEER: {e}")
        print("👉 Run 'steer ui', click 'Teach', and add a rule.")
"""

DEMO_2_CONTENT = """from steer import capture
from steer.verifiers import RegexVerifier

# Scenario: An agent summarizing customer tickets.
email_guard = RegexVerifier(
    name="PII Shield",
    pattern=r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}",
    fail_message="Output contains visible email address."
)

@capture(tags=["privacy_demo"], verifiers=[email_guard])
def summarize_ticket(ticket_text: str, steer_rules: str = ""):
    print(f"🤖 Summarizing ticket: {ticket_text}...")
    
    if steer_rules:
        print(f"   🧠 Context loaded: {steer_rules.strip()}")
        return "I have contacted [REDACTED] regarding the refund."
    else:
        print("   🧠 Context loaded: None")
        return "I have contacted user@example.com regarding the refund."

if __name__ == "__main__":
    print("--- ⚡ Steer: Safety Guard Demo ---")
    try:
        summarize_ticket("Ticket #994")
        print("\\n✅ SUCCESS: PII was redacted.")
    except Exception as e:
        print(f"\\n🚨 BLOCKED BY STEER: {e}")
        print("👉 Run 'steer ui', click 'Teach' on the Privacy failure.")
"""

DEMO_3_CONTENT = """from steer import capture
from steer.verifiers import AmbiguityVerifier

# Scenario: Travel agent searching for "Springfield".
logic_guard = AmbiguityVerifier(
    name="Business Logic Guard",
    tool_result_key="results",
    answer_key="message",
    threshold=3, 
    required_phrase="which state"
)

@capture(tags=["logic_demo"], verifiers=[logic_guard])
def find_location(query: str, steer_rules: str = ""):
    print(f"🤖 Searching for: {query}...")
    
    results = ["Springfield, IL", "Springfield, MA", "Springfield, MO", "Springfield, OR"]
    
    if steer_rules:
        print(f"   🧠 Context loaded: {steer_rules.strip()}")
        return {"message": "Multiple locations found. Which state?", "results": results}
    else:
        print("   🧠 Context loaded: None")
        return {"message": "I found Springfield, IL.", "results": results}

if __name__ == "__main__":
    print("--- ⚡ Steer: Logic Guard Demo ---")
    try:
        find_location("Springfield")
        print("\\n✅ SUCCESS: Agent asked for clarification.")
    except Exception as e:
        print(f"\\n🚨 BLOCKED BY STEER: {e}")
        print("👉 Run 'steer ui' and teach the agent to ask clarifying questions.")
"""

console = Console()

# --- DEMO CONTENT STRINGS ---

DEMO_1_CONTENT = """import json
from steer import capture, get_context
from steer.verifiers import JsonVerifier

# Scenario: An agent trying to output data for a frontend.
json_guard = JsonVerifier(name="Structure Guard")

@capture(tags=["format_demo"], verifiers=[json_guard])
def generate_user_profile(user_id: int):
    print(f"🤖 Generating profile for User {user_id}...")
    
    # Check if the user has taught the agent
    rules = get_context("format_demo")
    
    if rules:
        print("   🧠 Context loaded: Rules found! Applying fix...")
        return json.dumps({"id": 123, "name": "Alice", "active": True}, indent=2)
    else:
        print("   🧠 Context loaded: No rules found. Using default behavior.")
        return \"\"\"```json
{
    "id": 123,
    "name": "Alice",
    "active": true
}
```\"\"\"

if __name__ == "__main__":
    print("--- ⚡ Steer: Structure Guard Demo ---")
    try:
        generate_user_profile(123)
        print("\\n✅ SUCCESS: Agent output valid JSON.")
    except Exception as e:
        print(f"\\n🚨 BLOCKED BY STEER: {e}")
        print("👉 Run 'steer ui', click 'Teach', and add a rule.")
"""

DEMO_2_CONTENT = """from steer import capture, get_context
from steer.verifiers import RegexVerifier

# Scenario: An agent summarizing customer tickets.
email_guard = RegexVerifier(
    name="PII Shield",
    pattern=r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}",
    fail_message="Output contains visible email address."
)

@capture(tags=["privacy_demo"], verifiers=[email_guard])
def summarize_ticket(ticket_text: str):
    print(f"🤖 Summarizing ticket: {ticket_text}...")
    
    rules = get_context("privacy_demo")
    
    if rules:
        print("   🧠 Context loaded: Privacy rules active.")
        return "I have contacted [REDACTED] regarding the refund."
    else:
        print("   🧠 Context loaded: No privacy rules.")
        return "I have contacted user@example.com regarding the refund."

if __name__ == "__main__":
    print("--- ⚡ Steer: Safety Guard Demo ---")
    try:
        summarize_ticket("Ticket #994")
        print("\\n✅ SUCCESS: PII was redacted.")
    except Exception as e:
        print(f"\\n🚨 BLOCKED BY STEER: {e}")
        print("👉 Run 'steer ui', click 'Teach' on the Privacy failure.")
"""

DEMO_3_CONTENT = """from steer import capture, get_context
from steer.verifiers import AmbiguityVerifier

# Scenario: Travel agent searching for "Springfield".
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
    results = ["Springfield, IL", "Springfield, MA", "Springfield, MO", "Springfield, OR"]
    
    if rules:
        print("   🧠 Context loaded: Ambiguity rules active.")
        return {"message": "Multiple locations found. Which state?", "results": results}
    else:
        print("   🧠 Context loaded: No logic rules.")
        return {"message": "I found Springfield, IL.", "results": results}

if __name__ == "__main__":
    print("--- ⚡ Steer: Logic Guard Demo ---")
    try:
        find_location("Springfield")
        print("\\n✅ SUCCESS: Agent asked for clarification.")
    except Exception as e:
        print(f"\\n🚨 BLOCKED BY STEER: {e}")
        print("👉 Run 'steer ui' and teach the agent to ask clarifying questions.")
"""

def generate_demos():
    files = {
        "01_structure_guard.py": DEMO_1_CONTENT,
        "02_safety_guard.py": DEMO_2_CONTENT,
        "03_logic_guard.py": DEMO_3_CONTENT
    }
    
    console.print("\n[bold green]📦 Generating Steer Demos...[/bold green]")
    for filename, content in files.items():
        if not os.path.exists(filename):
            with open(filename, "w") as f:
                f.write(content)
            console.print(f"   Created [bold]{filename}[/bold]")
        else:
            console.print(f"   [dim]Skipped {filename} (exists)[/dim]")
            
    console.print("\n[bold]🚀 Ready![/bold] Run [green]python 01_structure_guard.py[/green] to start.")

def start_server(port=8000):
    url = f"http://localhost:{port}"
    console.print(f"\n[bold green]🚀 Steer Mission Control active at {url}[/bold green]")
    console.print("[dim]Press Ctrl+C to stop[/dim]\n")
    try:
        webbrowser.open(url)
    except:
        pass
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="error")

def main():
    parser = argparse.ArgumentParser(description="Steer AI - Active Reliability")
    parser.add_argument("command", nargs="?", help="Command to run ('ui' or 'init')")
    
    args = parser.parse_args()
    
    if args.command == "ui":
        start_server()
    elif args.command == "init":
        generate_demos()
    else:
        console.print("[bold]Steer AI[/bold] - The Active Reliability Layer")
        console.print("Run [green]steer init[/green] to generate examples.")
        console.print("Run [green]steer ui[/green] to start the dashboard.")

if __name__ == "__main__":
    main()