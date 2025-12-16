import json
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
        
        # New Community Hook (No email, just value)
        _print_community_hook()
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

def _print_community_hook():
    """
    Directs power users to GitHub Discussions instead of asking for email.
    """
    console.print("\n" + "-"*60)
    console.print("[bold]Next Step: Fine-Tuning[/bold]")
    console.print("You can upload this JSONL file directly to OpenAI or Anthropic.")
    console.print("\n[dim]Have questions or want to share your results?[/dim]")
    console.print("👉 Join the discussion: [link=https://github.com/imtt-dev/steer/discussions]https://github.com/imtt-dev/steer/discussions[/link]")
    console.print("-" * 60)