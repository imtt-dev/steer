import json
import time
from pathlib import Path
from typing import List, Dict, Any
from rich.console import Console
from .config import settings

console = Console()

def export_data(format_type: str = "openai", output_file: str = "steer_fine_tune.jsonl"):
    """
    Reads local Steer logs and converts successful runs into fine-tuning data.
    """
    log_path = settings.log_file
    if not log_path.exists():
        console.print("[red]No logs found. Run some agents first.[/red]")
        return

    exported_count = 0
    
    console.print(f"[dim]Reading local logs from {log_path}...[/dim]")

    with open(output_file, 'w', encoding='utf-8') as out_f:
        with open(log_path, 'r', encoding='utf-8') as in_f:
            for line in in_f:
                try:
                    record = json.loads(line)
                    
                    # LOGIC: Export "Golden Data"
                    # We export runs that passed verification. This provides the volume 
                    # needed for fine-tuning a model to behave correctly by default.
                    trace = record.get('trace', [])
                    is_blocked = any(step.get('type') == 'error' for step in trace)
                    
                    if not is_blocked:
                        user_content = _extract_input(record)
                        assistant_content = record.get('raw_outputs', '')

                        if user_content and assistant_content:
                            # OpenAI Chat Format
                            example = {
                                "messages": [
                                    {"role": "system", "content": f"You are a helpful agent. Context: {record.get('agent_name', 'default')}"},
                                    {"role": "user", "content": user_content},
                                    {"role": "assistant", "content": assistant_content}
                                ]
                            }
                            out_f.write(json.dumps(example) + "\n")
                            exported_count += 1
                except Exception as e:
                    continue

    if exported_count > 0:
        console.print(f"[bold green]Successfully exported {exported_count} training examples.[/bold green]")
        console.print(f"File created: [bold]{output_file}[/bold]")
        console.print("[dim]IMPORTANT: Review this file before uploading to OpenAI to ensure no PII/sensitive data is included.[/dim]")
        
        _trigger_email_capture()
    else:
        console.print("[yellow]No successful runs found to export.[/yellow]")

def _extract_input(record: dict) -> str:
    """Helper to get a clean user prompt string from the raw logs."""
    trace = record.get('trace', [])
    for step in trace:
        if step.get('type') == 'user':
            return step.get('content', '')
            
    raw_args = record.get('raw_inputs', {}).get('args', [])
    if raw_args:
        return str(raw_args[0])
        
    return "Unknown Input"

def _trigger_email_capture():
    """
    The 'Lock-in' Hook.
    Captures user interest in the Cloud Platform locally.
    """
    config_path = settings.steer_dir / "user_config.json"
    
    # If we already have their email, don't bug them
    if config_path.exists():
        return

    console.print("\n" + "-"*50)
    console.print("[bold]Steer Cloud (Private Beta)[/bold]")
    console.print("We are building a platform to automate this fine-tuning loop.")
    console.print("-" * 50)
    
    email = console.input("\nEnter email for early access: ")
    
    if email and "@" in email:
        # Save locally so we don't ask again
        with open(config_path, 'w') as f:
            json.dump({"email": email, "signup_date": time.time()}, f)
            
        console.print(f"[green]Added {email} to priority list.[/green]")
    else:
        console.print("[dim]Skipped.[/dim]")