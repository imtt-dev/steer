import sys
import uvicorn
import webbrowser
import argparse
import os
from steer.server import app

# --- DEMO 1: USER PROFILE AGENT ---
DEMO_1_CONTENT = """import json
from steer import capture, MockLLM
from steer.verifiers import JsonVerifier

# Scenario: An agent generating data for a frontend.
json_guard = JsonVerifier(name="Strict JSON")

@capture(tags=["profile_generator"], verifiers=[json_guard])
def generate_profile(request: str, steer_rules: str = ""):
    print(f"Processing request: '{request}'...")
    
    # 1. Steer automatically injects rules into 'steer_rules'
    # 2. We inject them into the System Prompt (Standard RAG/Agent pattern)
    system_prompt = f"You are a backend API. Output data based on the request.\\nReliability Rules: {steer_rules}"
    
    print(f"  System Prompt: {system_prompt.strip()}")

    # 3. Call Model (Mocked for demo, replace with OpenAI in prod)
    return MockLLM.call(system_prompt, request)

if __name__ == "__main__":
    print("--- Steer Demo: Profile Generator ---")
    try:
        generate_profile("Create active admin profile for Alice")
        print("\\nSUCCESS: Valid JSON returned.")
    except Exception as e:
        print(f"\\nBLOCKED BY STEER: {e}")
        print("Run 'steer ui' to fix the 'profile_generator'.")
"""

# --- DEMO 2: SUPPORT BOT ---
DEMO_2_CONTENT = """from steer import capture, MockLLM
from steer.verifiers import RegexVerifier

# Scenario: A support bot summarizing tickets.
email_guard = RegexVerifier(
    name="PII Shield",
    pattern=r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}",
    fail_message="Output contains visible email address."
)

@capture(tags=["support_bot"], verifiers=[email_guard])
def analyze_ticket(ticket_content: str, steer_rules: str = ""):
    print(f"Analyzing: '{ticket_content}'...")
    
    # Inject rules into context
    system_prompt = f"You are a helpful support agent.\\nSecurity Protocols: {steer_rules}"
    print(f"  System Prompt: {system_prompt.strip()}")
    
    return MockLLM.call(system_prompt, ticket_content)

if __name__ == "__main__":
    print("--- Steer Demo: Support Bot ---")
    try:
        analyze_ticket("Ticket #994: Refund request from Alice")
        print("\\nSUCCESS: PII was redacted.")
    except Exception as e:
        print(f"\\nBLOCKED BY STEER: {e}")
        print("Run 'steer ui' to fix the 'support_bot'.")
"""

# --- DEMO 3: WEATHER BOT ---
DEMO_3_CONTENT = """from steer import capture, MockLLM
from steer.verifiers import AmbiguityVerifier

# Scenario: A weather bot checking forecasts.
logic_guard = AmbiguityVerifier(
    name="Ambiguity Check",
    tool_result_key="results",
    answer_key="message",
    threshold=3, 
    required_phrase="which state"
)

@capture(tags=["weather_bot"], verifiers=[logic_guard])
def check_forecast(location: str, steer_rules: str = ""):
    print(f"Checking: '{location}'...")
    
    system_prompt = f"You are a weather bot.\\nPolicy: {steer_rules}"
    print(f"  System Prompt: {system_prompt.strip()}")
    
    return MockLLM.call(system_prompt, location)

if __name__ == "__main__":
    print("--- Steer Demo: Weather Bot ---")
    try:
        check_forecast("What is the weather in Springfield?")
        print("\\nSUCCESS: Bot asked for clarification.")
    except Exception as e:
        print(f"\\nBLOCKED BY STEER: {e}")
        print("Run 'steer ui' to fix the 'weather_bot'.")
"""

def generate_demos():
    files = {
        "01_structure_guard.py": DEMO_1_CONTENT,
        "02_safety_guard.py": DEMO_2_CONTENT,
        "03_logic_guard.py": DEMO_3_CONTENT
    }
    
    print("\nGenerating Steer examples...")
    for filename, content in files.items():
        if not os.path.exists(filename):
            with open(filename, "w") as f:
                f.write(content)
            print(f"  + Created {filename}")
        else:
            print(f"  - Skipped {filename} (exists)")
            
    print("\nReady. Run 'python 01_structure_guard.py' to start.")

def start_server(port=8000):
    url = f"http://localhost:{port}"
    print(f"\nSteer Mission Control active at {url}")
    print("Press Ctrl+C to stop\n")
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
        print("Steer AI - The Active Reliability Layer")
        print("Usage:")
        print("  steer init   Generate examples")
        print("  steer ui     Start dashboard")

if __name__ == "__main__":
    main()