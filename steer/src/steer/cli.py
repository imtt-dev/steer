import sys
import uvicorn
import webbrowser
import argparse
import os
from rich.console import Console
from steer.server import app
from steer.exporter import export_data 

console = Console()

# --- DEMO 1: USER PROFILE AGENT (JSON Structure) ---
DEMO_1_CONTENT = """import json
from steer import capture, MockLLM
from steer.judges import JsonJudge

json_guard = JsonJudge(name="Strict JSON")

@capture(tags=["profile_generator"], Judges=[json_guard])
def generate_profile(request: str, steer_rules: str = ""):
    print(f"Action: Processing request '{request}'")
    system_prompt = f"You are a backend API. Output data based on the request.\\nReliability Rules: {steer_rules}"
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
        print("Action Required: Run 'steer ui' to fix the 'profile_generator'.")
"""

# --- DEMO 2: SUPPORT BOT (Privacy) ---
DEMO_2_CONTENT = """from steer import capture, MockLLM
from steer.judges import RegexJudge

email_guard = RegexJudge(
    name="PII Shield",
    pattern=r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}",
    fail_message="Output contains visible email address."
)

@capture(tags=["support_bot"], Judges=[email_guard])
def analyze_ticket(ticket_content: str, steer_rules: str = ""):
    print(f"Action: Analyzing ticket '{ticket_content}'")
    system_prompt = f"You are a support agent.\\nSecurity Protocols: {steer_rules}"
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
"""

# --- DEMO 3: WEATHER BOT (Logic) ---
DEMO_3_CONTENT = """from steer import capture, MockLLM
from steer.judges import AmbiguityJudge

logic_guard = AmbiguityJudge(
    name="Ambiguity Check",
    tool_result_key="results",
    answer_key="message",
    threshold=3, 
    required_phrase="which state"
)

@capture(tags=["weather_bot"], Judges=[logic_guard])
def check_forecast(location: str, steer_rules: str = ""):
    print(f"Action: Checking weather for '{location}'")
    system_prompt = f"You are a weather bot.\\nPolicy: {steer_rules}"
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
"""

# --- DEMO 4: SLOP GUARD (Brand Voice) ---
DEMO_4_CONTENT = """from steer import capture, MockLLM
from steer.judges import SlopJudge

slop_guard = SlopJudge(name="Slop Filter")

@capture(tags=["brand_voice_agent"], Judges=[slop_guard])
def get_system_status(query: str, steer_rules: str = ""):
    print(f"Action: Generating response for '{query}'")
    system_prompt = f"You are a systems reporting service. Output raw status data.\\n{steer_rules}"
    print(f"Context: {system_prompt.strip()}")
    return MockLLM.call(system_prompt, query)

if __name__ == "__main__":
    print("--- Steer Demo: Slop Guard ---")
    try:
        get_system_status("Provide a status report on the server migration.")
        print("[+] Status: Passed")
    except Exception as e:
        print("[-] Status: Blocked")
        print(f"Reason: {e}")
"""

def generate_demos():
    files = {
        "01_structure_guard.py": DEMO_1_CONTENT,
        "02_safety_guard.py": DEMO_2_CONTENT,
        "03_logic_guard.py": DEMO_3_CONTENT,
        "04_slop_guard.py": DEMO_4_CONTENT
    }
    
    console.print("\n[bold green]Generating Steer examples...[/bold green]")
    for filename, content in files.items():
        if not os.path.exists(filename):
            with open(filename, "w") as f:
                f.write(content)
            console.print(f"  [green]+[/green] Created {filename}")
        else:
            console.print(f"  [dim]- Skipped {filename} (exists)[/dim]")
            
    console.print("\n[bold]Ready![/bold] Run [green]python 01_structure_guard.py[/green] to start.")

def start_server(port=8000):
    url = f"http://localhost:{port}"
    console.print(f"\n[bold green]Steer Mission Control active at {url}[/bold green]")
    console.print("[dim]Press Ctrl+C to stop[/dim]\n")
    try:
        webbrowser.open(url)
    except:
        pass
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="error")

def main():
    parser = argparse.ArgumentParser(description="Steer AI - Active Reliability")
    parser.add_argument("command", nargs="?", help="Command to run ('ui', 'init', 'export')")
    
    # Arguments for the export command
    parser.add_argument("--format", default="openai", help="Export format (default: openai)")
    # FIX: Change default from "steer_fine_tune.jsonl" to None
    parser.add_argument("--out", default=None, help="Output filename")
    
    args = parser.parse_args()
    
    if args.command == "ui":
        start_server()
    elif args.command == "init":
        generate_demos()
    elif args.command == "export":
        # Now passing None allows exporter.py to choose steer_dpo_train.jsonl for dpo
        export_data(format_type=args.format, output_file=args.out)
    else:
        console.print("[bold]Steer[/bold] - The Active Reliability Layer")
        console.print("Run [green]steer init[/green] to generate examples.")
        console.print("Run [green]steer ui[/green] to start the dashboard.")
        console.print("Run [green]steer export[/green] to create fine-tuning data.")

if __name__ == "__main__":
    main()